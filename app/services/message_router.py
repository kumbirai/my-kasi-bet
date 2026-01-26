"""
Message router service.

This module handles routing of incoming WhatsApp messages to appropriate
handlers based on user state and message content.
"""
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.deposit import PaymentMethod
from app.models.user import User
from app.models.wallet import Wallet
from app.models.withdrawal import WithdrawalMethod
from app.services.bet_service import (
    InsufficientBalanceError,
    InvalidBetAmountError,
    InvalidBetDataError,
)
from app.services.deposit_service import deposit_service
from app.services.games.color_game import ColorGame
from app.services.games.football_yesno import FootballYesNoGame
from app.services.games.lucky_wheel import LuckyWheelGame
from app.services.games.pick_3 import Pick3Game
from app.services.user_service import UserService
from app.services.wallet_service import wallet_service
from app.services.whatsapp import whatsapp_service
from app.services.withdrawal_service import withdrawal_service
from app.utils.helpers import clean_message_text, normalize_phone_number

logger = logging.getLogger(__name__)


class UserState:
    """User state constants for multi-step flows."""

    AWAITING_DEPOSIT_AMOUNT = "awaiting_deposit_amount"
    AWAITING_DEPOSIT_METHOD = "awaiting_deposit_method"
    AWAITING_DEPOSIT_PROOF = "awaiting_deposit_proof"
    AWAITING_WITHDRAWAL_AMOUNT = "awaiting_withdrawal_amount"
    AWAITING_WITHDRAWAL_METHOD = "awaiting_withdrawal_method"
    AWAITING_WITHDRAWAL_DETAILS = "awaiting_withdrawal_details"
    VIEWING_BALANCE_MENU = "viewing_balance_menu"
    VIEWING_GAMES_MENU = "viewing_games_menu"
    VIEWING_HELP_MENU = "viewing_help_menu"
    PICK3_SELECT_NUMBERS = "pick3_select_numbers"
    PICK3_ENTER_AMOUNT = "pick3_enter_amount"
    FOOTBALL_SELECT_MATCH = "football_select_match"
    FOOTBALL_SELECT_CHOICE = "football_select_choice"
    FOOTBALL_ENTER_AMOUNT = "football_enter_amount"
    LUCKY_WHEEL_SELECT_NUMBER = "lucky_wheel_select_number"
    LUCKY_WHEEL_ENTER_AMOUNT = "lucky_wheel_enter_amount"
    VIEWING_LUCKY_WHEEL_RESULT = "viewing_lucky_wheel_result"
    COLOR_GAME_SELECT_COLOR = "color_game_select_color"
    COLOR_GAME_ENTER_AMOUNT = "color_game_enter_amount"
    VIEWING_COLOR_GAME_RESULT = "viewing_color_game_result"
    VIEWING_PICK3_RESULT = "viewing_pick3_result"
    LUCKY_WHEEL_CONFIRM = "lucky_wheel_confirm"
    COLOR_GAME_CONFIRM = "color_game_confirm"
    PICK3_CONFIRM = "pick3_confirm"
    FOOTBALL_CONFIRM = "football_confirm"


class MessageRouter:
    """
    Routes incoming WhatsApp messages to appropriate handlers.

    This service manages the conversation flow, user registration,
    command parsing, and response generation.
    """

    def __init__(self) -> None:
        """
        Initialize message router.

        Sets up in-memory state storage for user conversation states.
        In production, this should be migrated to Redis.
        """
        self.user_states: Dict[int, Dict[str, Any]] = {}
        self.user_service = UserService()

    def _push_to_back_stack(self, user_id: int, state: str) -> None:
        """
        Push a state to the user's back stack.

        Args:
            user_id: User ID
            state: State to push to back stack
        """
        if user_id not in self.user_states:
            self.user_states[user_id] = {}
        
        if "back_stack" not in self.user_states[user_id]:
            self.user_states[user_id]["back_stack"] = []
        
        # Only push if state is not None and not empty
        if state:
            self.user_states[user_id]["back_stack"].append(state)

    def _pop_from_back_stack(self, user_id: int) -> Optional[str]:
        """
        Pop a state from the user's back stack.

        Args:
            user_id: User ID

        Returns:
            Previous state or None if stack is empty
        """
        if user_id not in self.user_states:
            return None
        
        back_stack = self.user_states[user_id].get("back_stack", [])
        if back_stack:
            return back_stack.pop()
        return None

    def _set_state(self, user_id: int, new_state: str, preserve_current: bool = True) -> None:
        """
        Set a new state and manage back stack.

        Args:
            user_id: User ID
            new_state: New state to set
            preserve_current: If True, push current state to back stack before setting new one
        """
        if user_id not in self.user_states:
            self.user_states[user_id] = {}
        
        if preserve_current:
            current_state = self.user_states[user_id].get("state")
            if current_state:
                self._push_to_back_stack(user_id, current_state)
        
        self.user_states[user_id]["state"] = new_state

    def _clear_state(self, user_id: int) -> None:
        """
        Clear user state and back stack.

        Args:
            user_id: User ID
        """
        if user_id in self.user_states:
            self.user_states.pop(user_id, None)

    def _validate_pick3_numbers(self, message: str) -> List[int]:
        """
        Validate exactly 3 numbers (1-36), no duplicates.

        Args:
            message: Message text containing numbers

        Returns:
            List of 3 validated numbers

        Raises:
            ValueError: If validation fails
        """
        numbers = re.findall(r"\d+", message)
        
        if len(numbers) != 3:
            raise ValueError("Please select exactly 3 numbers (1-36). Example: 7 14 23")
        
        try:
            selected_numbers = [int(n) for n in numbers]
        except ValueError:
            raise ValueError("Invalid numbers. Please enter 3 numbers between 1 and 36.")
        
        # Check for duplicates
        if len(selected_numbers) != len(set(selected_numbers)):
            raise ValueError("Duplicate numbers not allowed. Please select 3 different numbers.")
        
        # Validate range
        for num in selected_numbers:
            if num < 1 or num > 36:
                raise ValueError(f"Number {num} is out of range. Please select numbers between 1 and 36.")
        
        return selected_numbers

    def _validate_lucky_wheel_number(self, message: str) -> int:
        """
        Validate number 1-12 only.

        Args:
            message: Message text containing number

        Returns:
            Validated number (1-12)

        Raises:
            ValueError: If validation fails
        """
        try:
            number = int(message.strip())
        except ValueError:
            raise ValueError("Invalid input! Please enter a number between 1 and 12.")
        
        if number < 1 or number > 12:
            raise ValueError(f"Number {number} is out of range. Please select a number between 1 and 12.")
        
        return number

    def _validate_color(self, message: str) -> str:
        """
        Validate color input (accept R/Red, G/Green, B/Blue, Y/Yellow).

        Args:
            message: Message text containing color

        Returns:
            Validated color name (lowercase)

        Raises:
            ValueError: If validation fails
        """
        color_input = message.strip().lower()
        
        # Map shortcuts to full names
        color_map = {
            "r": "red",
            "g": "green",
            "b": "blue",
            "y": "yellow",
            "red": "red",
            "green": "green",
            "blue": "blue",
            "yellow": "yellow",
        }
        
        selected_color = color_map.get(color_input)
        
        if not selected_color:
            raise ValueError(
                "Invalid color! Please select: Red (R), Green (G), Blue (B), or Yellow (Y)."
            )
        
        return selected_color

    def _validate_stake(
        self, message: str, min_amount: Decimal, max_amount: Decimal
    ) -> Decimal:
        """
        Validate stake amount within limits.

        Args:
            message: Message text containing amount
            min_amount: Minimum allowed amount
            max_amount: Maximum allowed amount

        Returns:
            Validated stake amount

        Raises:
            ValueError: If validation fails
        """
        # Extract amount from message (handles "R50", "50", "R50.00", etc.)
        amount_match = re.search(r"r?(\d+(?:\.\d{1,2})?)", message.lower())
        
        if not amount_match:
            raise ValueError(f"Invalid amount format. Example: R{float(min_amount):.2f} or {float(min_amount):.0f}")
        
        try:
            stake_amount = Decimal(amount_match.group(1))
        except (ValueError, InvalidOperation):
            raise ValueError(f"Invalid amount. Please enter a number between R{float(min_amount):.2f} and R{float(max_amount):.2f}.")
        
        if stake_amount < min_amount:
            raise ValueError(f"Minimum bet is R{float(min_amount):.2f}. Please enter a valid amount.")
        
        if stake_amount > max_amount:
            raise ValueError(f"Maximum bet is R{float(max_amount):.2f}. Please enter a valid amount.")
        
        return stake_amount

    async def route_message(
        self,
        from_number: str,
        message_text: str,
        message_id: str,
        db: Session,
    ) -> None:
        """
        Route incoming WhatsApp message to appropriate handler.

        This is the main entry point for processing messages. It handles:
        - Message acknowledgment (mark as read)
        - User registration (if new user)
        - Command parsing and routing
        - Response generation and sending

        Args:
            from_number: Sender's phone number (format: 27821234567)
            message_text: Message content
            message_id: WhatsApp message ID
            db: Database session
        """
        normalized_phone: Optional[str] = None
        try:
            # Mark message as read (non-blocking)
            await whatsapp_service.mark_as_read(message_id)

            # Normalize phone number
            normalized_phone = normalize_phone_number(from_number)

            # Clean message
            clean_message = clean_message_text(message_text)

            # Check if user exists before creating
            existing_user = self.user_service.get_user_by_phone(normalized_phone, db)
            is_new_user = existing_user is None

            # Get or create user
            user = self.user_service.get_or_create_user(normalized_phone, db)

            # Check if user is blocked
            if user.is_blocked:
                response = (
                    "❌ Your account has been blocked. "
                    "Please contact support for assistance."
                )
                await whatsapp_service.send_message(
                    normalized_phone, response, reply_to_message_id=message_id
                )
                return

            # Update last active
            self.user_service.update_last_active(user, db)

            # Send welcome message for new users
            if is_new_user:
                response = self._get_welcome_message(user)
                await whatsapp_service.send_message(
                    normalized_phone, response, reply_to_message_id=message_id
                )
                return

            # Check if user has active state (multi-step flow)
            state = self.user_states.get(user.id)

            if state:
                response = await self._handle_state_flow(
                    user, clean_message, state, db
                )
            else:
                response = await self._handle_main_menu(user, clean_message, db)

            # Send response
            await whatsapp_service.send_message(
                normalized_phone, response, reply_to_message_id=message_id
            )

        except ValueError as e:
            logger.warning(f"Invalid phone number format: {e}")
            if normalized_phone:
                await whatsapp_service.send_message(
                    normalized_phone,
                    "❌ Invalid phone number format.\n\nReply 'menu' to restart.",
                )
        except Exception as e:
            logger.error(f"Error routing message: {e}", exc_info=True)
            if normalized_phone:
                try:
                    # Clear any broken state
                    user_id = None
                    if normalized_phone:
                        user = self.user_service.get_user_by_phone(normalized_phone, db)
                        if user:
                            user_id = user.id
                            self._clear_state(user_id)
                    
                    await whatsapp_service.send_message(
                        normalized_phone,
                        "❌ Something went wrong.\n\nReply 'menu' to restart.",
                    )
                except Exception as send_error:
                    logger.error(
                        f"Failed to send error message: {send_error}", exc_info=True
                    )

    def _get_welcome_message(self, user: User) -> str:
        """
        Generate welcome message for new users.

        Args:
            user: Newly registered user

        Returns:
            Welcome message text
        """
        return f"""🎉 Welcome to MyKasiBets!

You're all set! Your account has been created.

📱 Phone: {user.phone_number}
💰 Balance: R0.00

What would you like to do?

1️⃣ Check Balance
2️⃣ Play Games
3️⃣ Deposit Money
4️⃣ Help

Reply with the number of your choice."""

    def _get_breadcrumb(self, state: Optional[str] = None) -> str:
        """
        Get breadcrumb navigation string for current state.

        Args:
            state: Current user state (optional, for direct state lookup)

        Returns:
            Breadcrumb string showing user's location in menu tree
        """
        if not state:
            return "📍 Main Menu"

        breadcrumbs = {
            UserState.VIEWING_GAMES_MENU: "📍 Main Menu > Games",
            UserState.VIEWING_BALANCE_MENU: "📍 Main Menu > Balance",
            UserState.VIEWING_HELP_MENU: "📍 Main Menu > Help",
            UserState.LUCKY_WHEEL_SELECT_NUMBER: "📍 Main Menu > Games > Lucky Wheel > Select Number",
            UserState.LUCKY_WHEEL_ENTER_AMOUNT: "📍 Main Menu > Games > Lucky Wheel > Enter Amount",
            UserState.LUCKY_WHEEL_CONFIRM: "📍 Main Menu > Games > Lucky Wheel > Confirm",
            UserState.COLOR_GAME_SELECT_COLOR: "📍 Main Menu > Games > Color Game > Select Color",
            UserState.COLOR_GAME_ENTER_AMOUNT: "📍 Main Menu > Games > Color Game > Enter Amount",
            UserState.COLOR_GAME_CONFIRM: "📍 Main Menu > Games > Color Game > Confirm",
            UserState.VIEWING_COLOR_GAME_RESULT: "📍 Main Menu > Games > Color Game > Result",
            UserState.PICK3_SELECT_NUMBERS: "📍 Main Menu > Games > Pick 3 > Select Numbers",
            UserState.PICK3_ENTER_AMOUNT: "📍 Main Menu > Games > Pick 3 > Enter Amount",
            UserState.PICK3_CONFIRM: "📍 Main Menu > Games > Pick 3 > Confirm",
            UserState.VIEWING_PICK3_RESULT: "📍 Main Menu > Games > Pick 3 > Result",
            UserState.VIEWING_LUCKY_WHEEL_RESULT: "📍 Main Menu > Games > Lucky Wheel > Result",
            UserState.FOOTBALL_SELECT_MATCH: "📍 Main Menu > Games > Football Yes/No > Select Match",
            UserState.FOOTBALL_SELECT_CHOICE: "📍 Main Menu > Games > Football Yes/No > Select Choice",
            UserState.FOOTBALL_ENTER_AMOUNT: "📍 Main Menu > Games > Football Yes/No > Enter Amount",
            UserState.FOOTBALL_CONFIRM: "📍 Main Menu > Games > Football Yes/No > Confirm",
        }

        return breadcrumbs.get(state, "📍 Main Menu")

    async def _handle_main_menu(
        self, user: User, message: str, db: Session
    ) -> str:
        """
        Handle main menu selections.

        Parses user commands and routes to appropriate handlers.

        Args:
            user: User instance
            message: Cleaned message text
            db: Database session

        Returns:
            Response message text
        """
        message_lower = message.lower().strip()

        # Check for global commands first
        global_response = await self._handle_global_command(user, message, None, db)
        if global_response is not None:
            return global_response

        # Pick 3 command - check if user is in Pick 3 flow
        state = self.user_states.get(user.id)
        if state and state.get("state") in [
            UserState.PICK3_SELECT_NUMBERS,
            UserState.PICK3_ENTER_AMOUNT,
            UserState.PICK3_CONFIRM,
        ]:
            return await self._handle_pick3_flow(user, message, state, db)

        # Pick 3 start command
        if message_lower in ["pick3", "pick 3"]:
            return await self._start_pick3_flow(user)

        # Football Yes/No command - check if user is in Football flow
        state = self.user_states.get(user.id)
        if state and state.get("state") in [
            UserState.FOOTBALL_SELECT_MATCH,
            UserState.FOOTBALL_SELECT_CHOICE,
            UserState.FOOTBALL_ENTER_AMOUNT,
            UserState.FOOTBALL_CONFIRM,
        ]:
            return await self._handle_football_yesno_flow(user, message, state, db)

        # Football Yes/No start command
        if message_lower in ["football"]:
            return await self._start_football_yesno_flow(user, db)

        # Command mappings
        commands: Dict[str, Any] = {
            "1": lambda: self._check_balance(user, db),
            "2": lambda: self._show_games(user),
            "3": lambda: self._start_deposit_flow(user),
            "4": lambda: self._show_help(user),
            "start": lambda: self._show_main_menu(),
            "wheel": lambda: self._show_lucky_wheel_instructions(),
            "color": lambda: self._show_color_game_instructions(),
        }

        handler = commands.get(message_lower)

        if handler:
            result = handler()
            # Handle both sync and async handlers
            if hasattr(result, "__await__"):
                return await result
            return result
        else:
            return (
                "❌ Invalid option. Reply 'menu' to see available options "
                "or 'help' for assistance."
            )

    def _check_balance(self, user: User, db: Session) -> str:
        """
        Get user's wallet balance.

        Args:
            user: User instance
            db: Database session

        Returns:
            Balance information message
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
        balance = wallet.balance if wallet else Decimal("0.00")

        # Set state to track that user is viewing balance sub-menu
        self._set_state(user.id, UserState.VIEWING_BALANCE_MENU, preserve_current=False)

        return f"""💰 Your Balance: R{float(balance):.2f}

What would you like to do?

1️⃣ Play Games
2️⃣ Deposit Money
3️⃣ Withdraw Money
0️⃣ Back to Menu

Reply with number."""

    def _show_games(self, user: Optional[User] = None) -> str:
        """
        Show available games.

        Args:
            user: Optional user instance to track menu state

        Returns:
            Games menu message
        """
        # Track that user is viewing games menu
        if user:
            self._set_state(user.id, UserState.VIEWING_GAMES_MENU, preserve_current=False)

        breadcrumb = self._get_breadcrumb(UserState.VIEWING_GAMES_MENU)
        return f"""{breadcrumb}

🎮 CHOOSE YOUR GAME:

1️⃣ Lucky Wheel (1-12) - Win 10x
2️⃣ Color Game - Win 3x
3️⃣ Pick 3 Numbers - Win 800x
4️⃣ Football Yes/No - Various odds
0️⃣ Back to Menu

Reply with game number."""

    async def _start_deposit_flow(self, user: User) -> str:
        """
        Start deposit flow.

        Args:
            user: User instance

        Returns:
            Deposit initiation message
        """
        # Set new state and push current to back stack
        self._set_state(user.id, UserState.AWAITING_DEPOSIT_AMOUNT, preserve_current=True)

        return """💰 DEPOSIT MONEY

Minimum deposit: R10
Maximum deposit: R10,000

How much would you like to deposit?
Example: 50 (for R50)

Reply '0' or 'b' to go back."""

    def _show_help(self, user: Optional[User] = None) -> str:
        """
        Show help information.

        Args:
            user: Optional user instance to track menu state

        Returns:
            Help message
        """
        # Track that user is viewing help menu
        if user:
            self._set_state(user.id, UserState.VIEWING_HELP_MENU, preserve_current=False)

        return """❓ HELP & COMMANDS:

'menu' - Main menu
'balance' - Check balance
'games' - See all games
'deposit' - Deposit info
'withdraw' - Withdrawal info
'help' - This message

📞 Support: support@mykasibets.com
⏰ Available 24/7

Reply '0' or 'b' to go back."""

    def _show_main_menu(self) -> str:
        """
        Show main menu.

        Returns:
            Main menu message
        """
        return """📱 MAIN MENU:

1️⃣ Check Balance
2️⃣ Play Games
3️⃣ Deposit Money
4️⃣ Help

Reply with number."""

    def _is_global_command(self, message: str, current_state: Optional[str] = None) -> bool:
        """
        Check if message is a global command.

        Args:
            message: Message text
            current_state: Current user state (for special cases)

        Returns:
            True if message is a global command
        """
        message_lower = message.lower().strip()
        
        # Special case: In COLOR_GAME_SELECT_COLOR, "b" is a valid color (blue)
        # So "b" is NOT a global command in that state
        if current_state == UserState.COLOR_GAME_SELECT_COLOR:
            global_commands = ["menu", "help", "balance", "games", "deposit", "withdraw", "0", "back"]
        else:
            global_commands = ["menu", "help", "balance", "games", "deposit", "withdraw", "0", "b", "back"]
        
        return message_lower in global_commands

    async def _handle_global_command(
        self,
        user: User,
        message: str,
        state: Optional[Dict[str, Any]],
        db: Session,
    ) -> Optional[str]:
        """
        Handle global commands that work from any screen.

        Args:
            user: User instance
            message: Message text
            state: Current user state (optional)
            db: Database session

        Returns:
            Response message if command was handled, None otherwise
        """
        message_lower = message.lower().strip()
        current_state = state.get("state") if state else None

        if message_lower == "menu":
            self._clear_state(user.id)
            return self._show_main_menu()
        
        elif message_lower in ["0", "b", "back"]:
            # Special case: In COLOR_GAME_SELECT_COLOR, "b" is a valid color (blue)
            # So we only handle "0" and "back" in that state
            if current_state == UserState.COLOR_GAME_SELECT_COLOR:
                if message_lower in ["0", "back"]:
                    return await self._handle_back_navigation(user, state, db)
                return None  # "b" is not a global command here
            else:
                if state:
                    return await self._handle_back_navigation(user, state, db)
                else:
                    self._clear_state(user.id)
                    return self._show_main_menu()
        
        elif message_lower == "help":
            if user:
                self._set_state(user.id, UserState.VIEWING_HELP_MENU, preserve_current=False)
            return self._show_help(user)
        
        elif message_lower == "balance":
            return self._check_balance(user, db)
        
        elif message_lower == "games":
            return self._show_games(user)
        
        elif message_lower == "deposit":
            return await self._start_deposit_flow(user)
        
        elif message_lower == "withdraw":
            return await self._start_withdrawal_flow(user, db)
        
        return None  # Not a global command

    async def _handle_state_flow(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle multi-step conversation flows.

        This method handles complex flows like deposits, withdrawals, etc.

        Args:
            user: User instance
            message: Cleaned message text
            state: Current user state
            db: Database session

        Returns:
            Response message text
        """
        message_lower = message.lower().strip()
        current_state = state.get("state") if state else None

        # Check for global commands first (must work from any screen)
        if self._is_global_command(message, current_state):
            global_response = await self._handle_global_command(user, message, state, db)
            if global_response is not None:
                return global_response

        # Handle cancel - go back one step or to main menu
        if message_lower in ["cancel", "c"]:
            return await self._handle_cancel(user, state, db)

        if current_state == UserState.VIEWING_BALANCE_MENU:
            return await self._handle_balance_menu(user, message, state, db)
        elif current_state == UserState.VIEWING_GAMES_MENU:
            return await self._handle_games_menu(user, message, state, db)
        elif current_state == UserState.VIEWING_HELP_MENU:
            return await self._handle_help_menu(user, message, state, db)
        elif current_state == UserState.AWAITING_DEPOSIT_AMOUNT:
            return await self._handle_deposit_amount(user, message, state, db)
        elif current_state == UserState.AWAITING_DEPOSIT_METHOD:
            return await self._handle_deposit_method(user, message, state, db)
        elif current_state == UserState.AWAITING_DEPOSIT_PROOF:
            return await self._handle_deposit_proof(user, message, state, db)
        elif current_state == UserState.AWAITING_WITHDRAWAL_AMOUNT:
            return await self._handle_withdrawal_amount(user, message, state, db)
        elif current_state == UserState.AWAITING_WITHDRAWAL_METHOD:
            return await self._handle_withdrawal_method(user, message, state, db)
        elif current_state == UserState.AWAITING_WITHDRAWAL_DETAILS:
            return await self._handle_withdrawal_details(user, message, state, db)
        elif current_state in [
            UserState.PICK3_SELECT_NUMBERS,
            UserState.PICK3_ENTER_AMOUNT,
            UserState.PICK3_CONFIRM,
        ]:
            return await self._handle_pick3_flow(user, message, state, db)
        elif current_state in [
            UserState.FOOTBALL_SELECT_MATCH,
            UserState.FOOTBALL_SELECT_CHOICE,
            UserState.FOOTBALL_ENTER_AMOUNT,
            UserState.FOOTBALL_CONFIRM,
        ]:
            return await self._handle_football_yesno_flow(user, message, state, db)
        elif current_state in [
            UserState.LUCKY_WHEEL_SELECT_NUMBER,
            UserState.LUCKY_WHEEL_ENTER_AMOUNT,
            UserState.LUCKY_WHEEL_CONFIRM,
        ]:
            return await self._handle_lucky_wheel_flow(user, message, state, db)
        elif current_state in [
            UserState.COLOR_GAME_SELECT_COLOR,
            UserState.COLOR_GAME_ENTER_AMOUNT,
            UserState.COLOR_GAME_CONFIRM,
        ]:
            return await self._handle_color_game_flow(user, message, state, db)
        elif current_state in [
            UserState.VIEWING_LUCKY_WHEEL_RESULT,
            UserState.VIEWING_COLOR_GAME_RESULT,
            UserState.VIEWING_PICK3_RESULT,
        ]:
            return await self._handle_game_result(user, message, state, db)
        else:
            # Unknown state, clear and return to main menu
            self._clear_state(user.id)
            return await self._handle_main_menu(user, message, db)

    async def _handle_balance_menu(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle balance sub-menu selections.

        Args:
            user: User instance
            message: Menu selection
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        message_stripped = message.strip()

        # Route to appropriate handler based on selection
        if message_stripped == "1":
            # Clear balance menu state before showing games
            self.user_states.pop(user.id, None)
            return self._show_games(user)
        elif message_stripped == "2":
            # Clear balance menu state before starting deposit
            self.user_states.pop(user.id, None)
            return await self._start_deposit_flow(user)
        elif message_stripped == "3":
            # Clear balance menu state before starting withdrawal
            self.user_states.pop(user.id, None)
            return await self._start_withdrawal_flow(user, db)
        elif message_stripped in ["0", "b", "back"]:
            # Clear the balance menu state and return to main menu
            self.user_states.pop(user.id, None)
            return self._show_main_menu()
        else:
            # Invalid option, show balance menu again
            return self._check_balance(user, db)

    async def _handle_games_menu(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle games menu selections.

        Args:
            user: User instance
            message: Menu selection
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        message_stripped = message.strip().lower()

        # Route to appropriate handler based on selection
        if message_stripped in ["1", "wheel"]:
            # Start Lucky Wheel flow
            self.user_states.pop(user.id, None)
            return await self._start_lucky_wheel_flow(user)
        elif message_stripped in ["2", "color"]:
            # Start Color Game flow
            self.user_states.pop(user.id, None)
            return await self._start_color_game_flow(user)
        elif message_stripped in ["3", "pick3", "pick 3"]:
            # Clear games menu state before starting pick3
            self.user_states.pop(user.id, None)
            return await self._start_pick3_flow(user)
        elif message_stripped in ["4", "football"]:
            # Clear games menu state before starting football
            self.user_states.pop(user.id, None)
            return await self._start_football_yesno_flow(user, db)
        elif message_stripped in ["0", "b", "back"]:
            # Clear games menu state and return to main menu
            self.user_states.pop(user.id, None)
            return self._show_main_menu()
        else:
            # Invalid option, show games menu again
            return self._show_games(user)

    async def _handle_help_menu(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle help menu selections.

        Args:
            user: User instance
            message: Menu selection
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        message_stripped = message.strip().lower()

        # Handle back navigation
        if message_stripped in ["0", "b", "back"]:
            # Clear help menu state and return to main menu
            self.user_states.pop(user.id, None)
            return self._show_main_menu()
        else:
            # Invalid option or any other input, show help menu again
            return self._show_help(user)

    async def _handle_game_result(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle game result screen selections.

        Args:
            user: User instance
            message: Menu selection
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        message_stripped = message.strip().lower()
        current_state = state.get("state")
        game = state.get("game", "")

        # Handle back navigation
        if message_stripped in ["0", "b", "back"]:
            return await self._handle_back_navigation(user, state, db)

        # Handle play again (option 1)
        if message_stripped == "1":
            self.user_states.pop(user.id, None)
            if game == "lucky_wheel":
                return await self._start_lucky_wheel_flow(user)
            elif game == "color_game":
                return await self._start_color_game_flow(user)
            elif game == "pick3":
                return await self._start_pick3_flow(user)
            else:
                # Unknown game, go to games menu
                return self._show_games(user)

        # Handle games menu (option 2)
        elif message_stripped == "2":
            self.user_states.pop(user.id, None)
            return self._show_games(user)

        # Invalid option, show result again with options
        else:
            breadcrumb = self._get_breadcrumb(current_state)
            if current_state == UserState.VIEWING_LUCKY_WHEEL_RESULT:
                return f"""{breadcrumb}

❌ Invalid option.

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
            elif current_state == UserState.VIEWING_COLOR_GAME_RESULT:
                return f"""{breadcrumb}

❌ Invalid option.

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
            elif current_state == UserState.VIEWING_PICK3_RESULT:
                return f"""{breadcrumb}

❌ Invalid option.

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
            else:
                # Fallback
                self.user_states.pop(user.id, None)
                return self._show_games(user)

    async def _handle_deposit_amount(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle deposit amount input.

        Args:
            user: User instance
            message: Amount input
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        try:
            amount = Decimal(message.strip())

            if amount < 10:
                return "❌ Minimum deposit is R10. Please enter a valid amount:"

            if amount > 10000:
                return "❌ Maximum deposit is R10,000. Please enter a valid amount:"

            # Store amount in state and move to next step
            state["amount"] = amount
            self._set_state(user.id, UserState.AWAITING_DEPOSIT_METHOD, preserve_current=True)

            return f"""💳 PAYMENT METHOD

Amount: R{float(amount):.2f}

Choose your payment method:

1️⃣ 1Voucher
2️⃣ SnapScan
3️⃣ Capitec
4️⃣ Bank Transfer

Reply with the number (1-4) or '0'/'b' to go back."""

        except (ValueError, InvalidOperation):
            return "❌ Invalid amount. Please enter a number (e.g., 50):"

    async def _handle_deposit_method(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle payment method selection.

        Args:
            user: User instance
            message: Method selection
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        message_stripped = message.strip().lower()
        
        # Handle back navigation
        if message_stripped in ["0", "b", "back"]:
            return await self._handle_back_navigation(user, state, db)
        
        method_map = {
            "1": (PaymentMethod.VOUCHER_1, "1Voucher"),
            "2": (PaymentMethod.SNAPSCAN, "SnapScan"),
            "3": (PaymentMethod.CAPITEC, "Capitec"),
            "4": (PaymentMethod.BANK_TRANSFER, "Bank Transfer"),
        }

        method_info = method_map.get(message.strip())

        if not method_info:
            return "❌ Invalid choice. Please reply with a number (1-4) or '0'/'b' to go back:"

        payment_method, method_name = method_info

        amount = state["amount"]

        # Create deposit ticket immediately when method is selected
        try:
            deposit = deposit_service.create_deposit_request(
                user_id=user.id,
                amount=amount,
                payment_method=payment_method,
                proof_type=None,  # Proof not yet received
                proof_value=None,
                notes=f"Deposit via {method_name} - awaiting proof",
                db=db,
            )
            db.commit()

            # Store method and deposit_id in state and move to next step
            state["payment_method"] = payment_method
            state["method_name"] = method_name
            state["deposit_id"] = deposit.id
            self._set_state(user.id, UserState.AWAITING_DEPOSIT_PROOF, preserve_current=True)

            # Provide payment instructions based on method
            instructions = self._get_payment_instructions(payment_method, amount)

            return f"""{instructions}

Deposit ID: #{deposit.id}

Once you've made the payment, send us the proof:
📸 Send payment reference number or screenshot

Example: "REF123456" or attach image

Reply '0' or 'b' to go back."""

        except Exception as e:
            logger.error(f"Error creating deposit ticket: {e}", exc_info=True)
            self._clear_state(user.id)
            return f"""❌ Error creating deposit request: {str(e)}

Reply 'menu' to restart."""

    def _get_payment_instructions(
        self, method: PaymentMethod, amount: Decimal
    ) -> str:
        """
        Get payment instructions for specific method.

        Args:
            method: Payment method
            amount: Deposit amount

        Returns:
            Payment instructions
        """
        if method == PaymentMethod.VOUCHER_1:
            return f"""💳 1VOUCHER PAYMENT

Amount: R{float(amount):.2f}

Buy a 1Voucher at any retailer
Then send us the voucher PIN"""

        elif method == PaymentMethod.SNAPSCAN:
            return f"""📱 SNAPSCAN PAYMENT

Amount: R{float(amount):.2f}

Scan this SnapScan code: [QR CODE]
Or use SnapScan to: 0821234567"""

        elif method == PaymentMethod.CAPITEC:
            return f"""🏦 CAPITEC PAYMENT

Amount: R{float(amount):.2f}

Send to: +27 82 123 4567
Name: MyKasiBets"""

        elif method == PaymentMethod.BANK_TRANSFER:
            return f"""🏦 BANK TRANSFER

Amount: R{float(amount):.2f}

Bank: FNB
Account: 1234567890
Branch: 250655
Account Type: Cheque
Reference: Your phone number"""

        return "Payment instructions will be provided."

    async def _handle_deposit_proof(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle deposit proof submission.

        Args:
            user: User instance
            message: Proof of payment
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        amount = state["amount"]
        payment_method = state["payment_method"]
        method_name = state["method_name"]
        deposit_id = state.get("deposit_id")

        # Update existing deposit with proof
        try:
            if not deposit_id:
                # Fallback: create new deposit if deposit_id is missing
                deposit = deposit_service.create_deposit_request(
                    user_id=user.id,
                    amount=amount,
                    payment_method=payment_method,
                    proof_type="reference_number",
                    proof_value=message.strip(),
                    notes="Submitted via WhatsApp",
                    db=db,
                )
                db.commit()
            else:
                # Update existing deposit with proof
                from app.models.deposit import Deposit
                deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
                if not deposit:
                    raise ValueError(f"Deposit {deposit_id} not found")
                
                deposit.proof_type = "reference_number"
                deposit.proof_value = message.strip()
                deposit.notes = f"Proof received via WhatsApp: {message.strip()}"
                db.commit()

            # Clear state
            self._clear_state(user.id)

            return f"""✅ DEPOSIT REQUEST SUBMITTED

Deposit ID: #{deposit.id}
Amount: R{float(amount):.2f}
Method: {method_name}
Proof: Received ✓

Your deposit is being reviewed.
You'll receive a notification within 5-30 minutes.

Reply 'menu' for main menu."""

        except ValueError as e:
            logger.error(f"Error creating deposit request: {e}", exc_info=True)
            self._clear_state(user.id)
            return f"""❌ {str(e)}

Reply 'menu' to restart."""
        except Exception as e:
            logger.error(f"Error creating deposit request: {e}", exc_info=True)
            self._clear_state(user.id)
            return f"""❌ Error submitting deposit request: {str(e)}

Reply 'menu' to restart."""

    async def _start_withdrawal_flow(self, user: User, db: Session) -> str:
        """
        Start withdrawal flow.

        Args:
            user: User instance
            db: Database session

        Returns:
            Withdrawal initiation message
        """
        # Check minimum balance
        try:
            balance = wallet_service.get_balance(user.id, db)
            if balance < withdrawal_service.MIN_WITHDRAWAL:
                return f"""❌ INSUFFICIENT BALANCE

Your balance: R{float(balance):.2f}
Minimum withdrawal: R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}

Please deposit more funds or play games to win!
Reply 'menu' for main menu."""

            # Set new state and push current to back stack
            self._set_state(user.id, UserState.AWAITING_WITHDRAWAL_AMOUNT, preserve_current=True)

            return f"""💸 WITHDRAW MONEY

Your balance: R{float(balance):.2f}

Minimum: R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}
Maximum: R{float(withdrawal_service.MAX_WITHDRAWAL):.2f}

How much would you like to withdraw?
Example: 100 (for R100)

Reply '0' or 'b' to go back."""

        except Exception as e:
            logger.error(f"Error starting withdrawal flow: {e}")
            return "❌ Error checking balance. Please try again later."

    async def _handle_withdrawal_amount(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle withdrawal amount input.

        Args:
            user: User instance
            message: Amount input
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        try:
            amount = Decimal(message.strip())

            # Validate amount
            if amount < withdrawal_service.MIN_WITHDRAWAL:
                return f"❌ Minimum withdrawal is R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}. Please enter a valid amount:"

            if amount > withdrawal_service.MAX_WITHDRAWAL:
                return f"❌ Maximum withdrawal is R{float(withdrawal_service.MAX_WITHDRAWAL):.2f}. Please enter a valid amount:"

            # Check balance
            balance = wallet_service.get_balance(user.id, db)
            if amount > balance:
                return f"❌ Insufficient balance. You have R{float(balance):.2f}. Please enter a valid amount:"

            # Store amount and move to next step
            state["amount"] = amount
            self._set_state(user.id, UserState.AWAITING_WITHDRAWAL_METHOD, preserve_current=True)

            return f"""💳 WITHDRAWAL METHOD

Amount: R{float(amount):.2f}

Choose withdrawal method:

1️⃣ Bank Transfer (2-3 days)
2️⃣ Cash Pickup (24 hours)
3️⃣ eWallet (Instant)

Reply with the number (1-3) or '0'/'b' to go back."""

        except (ValueError, InvalidOperation):
            return "❌ Invalid amount. Please enter a number (e.g., 100):"

    async def _handle_withdrawal_method(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle withdrawal method selection.

        Args:
            user: User instance
            message: Method selection
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        message_stripped = message.strip().lower()
        
        # Handle back navigation
        if message_stripped in ["0", "b", "back"]:
            return await self._handle_back_navigation(user, state, db)
        
        method_map = {
            "1": (WithdrawalMethod.BANK_TRANSFER, "Bank Transfer"),
            "2": (WithdrawalMethod.CASH_PICKUP, "Cash Pickup"),
            "3": (WithdrawalMethod.EWALLET, "eWallet"),
        }

        method_info = method_map.get(message.strip())

        if not method_info:
            return "❌ Invalid choice. Please reply with a number (1-3) or '0'/'b' to go back:"

        withdrawal_method, method_name = method_info

        state["withdrawal_method"] = withdrawal_method
        state["method_name"] = method_name
        self._set_state(user.id, UserState.AWAITING_WITHDRAWAL_DETAILS, preserve_current=True)

        if withdrawal_method == WithdrawalMethod.BANK_TRANSFER:
            return """🏦 BANK DETAILS

Please provide your bank details in this format:

Bank Name
Account Number
Account Holder Name

Example:
FNB
1234567890
John Doe

Reply '0' or 'b' to go back."""

        elif withdrawal_method == WithdrawalMethod.CASH_PICKUP:
            return """📍 PICKUP LOCATION

Cash pickup locations:
- Johannesburg CBD
- Pretoria Central
- Cape Town City Center

Which location is convenient for you?

Reply '0' or 'b' to go back."""

        else:  # eWallet
            return """📱 EWALLET DETAILS

Please provide your cellphone number for eWallet:

Example: 0821234567

Reply '0' or 'b' to go back."""

    async def _handle_withdrawal_details(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle withdrawal details submission.

        Args:
            user: User instance
            message: Withdrawal details
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        amount = state["amount"]
        withdrawal_method = state["withdrawal_method"]
        method_name = state["method_name"]

        # Parse details based on method
        try:
            if withdrawal_method == WithdrawalMethod.BANK_TRANSFER:
                lines = [line.strip() for line in message.strip().split("\n") if line.strip()]
                if len(lines) < 3:
                    return "❌ Please provide all bank details (Bank, Account Number, Account Holder):"

                bank_name = lines[0]
                account_number = lines[1]
                account_holder = lines[2]
            else:
                bank_name = None
                account_number = message.strip()
                account_holder = None

            # Create withdrawal request
            withdrawal = withdrawal_service.create_withdrawal_request(
                user_id=user.id,
                amount=amount,
                withdrawal_method=withdrawal_method,
                bank_name=bank_name,
                account_number=account_number,
                account_holder=account_holder,
                notes="Submitted via WhatsApp",
                db=db,
            )

            db.commit()

            # Clear state
            self.user_states.pop(user.id, None)

            # Get new balance
            new_balance = wallet_service.get_balance(user.id, db)

            return f"""✅ WITHDRAWAL REQUEST SUBMITTED

Withdrawal ID: #{withdrawal.id}
Amount: R{float(amount):.2f}
Method: {method_name}
New Balance: R{float(new_balance):.2f}

Your request is being reviewed.
Processing time: 24-48 hours

You'll receive a notification once approved.

Reply 'menu' for main menu."""

        except ValueError as e:
            logger.error(f"Error creating withdrawal request: {e}", exc_info=True)
            self._clear_state(user.id)
            return f"""❌ {str(e)}

Reply 'menu' to restart."""
        except Exception as e:
            logger.error(f"Error creating withdrawal request: {e}", exc_info=True)
            self._clear_state(user.id)
            return f"""❌ Error submitting withdrawal request: {str(e)}

Reply 'menu' to restart."""

    async def _start_lucky_wheel_flow(self, user: User) -> str:
        """
        Start Lucky Wheel game flow.

        Args:
            user: User instance

        Returns:
            Number selection prompt message
        """
        # Set new state and push current to back stack
        self._set_state(user.id, UserState.LUCKY_WHEEL_SELECT_NUMBER, preserve_current=True)
        self.user_states[user.id]["game"] = "lucky_wheel"

        breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_SELECT_NUMBER)
        return f"""{breadcrumb}

🎡 LUCKY WHEEL (1-12)
Win 10x your bet!

Select a number (1-12):

Reply '0' or 'b' to go back."""

    async def _handle_lucky_wheel_flow(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle Lucky Wheel multi-step conversation.

        Args:
            user: User instance
            message: Message text
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        step = state.get("state")

        if step == UserState.LUCKY_WHEEL_SELECT_NUMBER:
            # User is selecting a number
            try:
                selected_number = self._validate_lucky_wheel_number(message)

                # Save to state and move to next step
                state["selected_number"] = selected_number
                state["game"] = "lucky_wheel"
                self._set_state(user.id, UserState.LUCKY_WHEEL_ENTER_AMOUNT, preserve_current=True)

                breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_ENTER_AMOUNT)
                return f"""{breadcrumb}

✅ Your number: {selected_number}

Enter bet amount (R5-R500):
Example: R50 or 50

Reply '0' or 'b' to go back."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_SELECT_NUMBER)
                return f"""{breadcrumb}

❌ {str(e)}

🎡 LUCKY WHEEL (1-12)
Select a number (1-12):

Reply '0' or 'b' to go back."""

        elif step == UserState.LUCKY_WHEEL_ENTER_AMOUNT:
            # User is entering bet amount
            try:
                stake_amount = self._validate_stake(message, Decimal("5.00"), Decimal("500.00"))
                selected_number = state["selected_number"]

                # Store stake and move to confirmation
                state["stake_amount"] = stake_amount
                state["game"] = "lucky_wheel"
                self._set_state(user.id, UserState.LUCKY_WHEEL_CONFIRM, preserve_current=True)

                # Calculate potential payout
                potential_payout = stake_amount * Decimal("10.0")
                
                # Get current balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")

                breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_CONFIRM)
                return f"""{breadcrumb}

✅ CONFIRM YOUR BET

Game: Lucky Wheel
Your pick: Number {selected_number}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f} (10x)

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R5-R500):
Example: R50 or 50

Reply '0' or 'b' to go back."""

        elif step == UserState.LUCKY_WHEEL_CONFIRM:
            # User is confirming or cancelling bet
            message_lower = message.lower().strip()
            
            if message_lower in ["no", "n", "cancel"]:
                # User cancelled - go back to amount entry
                state.pop("stake_amount", None)
                state["state"] = UserState.LUCKY_WHEEL_ENTER_AMOUNT
                breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_ENTER_AMOUNT)
                return f"""{breadcrumb}

✅ Your number: {state['selected_number']}

Enter bet amount (R5-R500):
Example: R50 or 50

Reply '0' or 'b' to go back."""
            
            elif message_lower not in ["yes", "y", "confirm"]:
                # Invalid confirmation response
                breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_CONFIRM)
                selected_number = state["selected_number"]
                stake_amount = state["stake_amount"]
                potential_payout = stake_amount * Decimal("10.0")
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                return f"""{breadcrumb}

❌ Invalid response. Please reply 'yes' to confirm or 'no' to cancel.

✅ CONFIRM YOUR BET

Game: Lucky Wheel
Your pick: Number {selected_number}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f} (10x)

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""
            
            # User confirmed - place bet
            try:
                stake_amount = state["stake_amount"]
                selected_number = state["selected_number"]

                # Check balance before placing bet
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                if current_balance < stake_amount:
                    breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_CONFIRM)
                    return f"""{breadcrumb}

❌ Insufficient balance! You have R{float(current_balance):.2f}, but need R{float(stake_amount):.2f}.

Reply 'no' to cancel or 'menu' to go to main menu."""

                # Play the game
                bet, result = await LuckyWheelGame.play(
                    user_id=user.id,
                    stake_amount=stake_amount,
                    bet_data={"selected_number": selected_number},
                    db=db,
                )

                # Get new balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                new_balance = wallet.balance if wallet else Decimal("0.00")

                # Send bet receipt
                receipt_message = f"""✅ BET PLACED

Bet ID: #{bet.id}
Game: Lucky Wheel
Your pick: Number {selected_number}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(stake_amount * Decimal("10.0")):.2f} (10x)

Round ID: #{bet.id}
Balance: R{float(new_balance):.2f}

Wait for result!"""

                # Set state to show result with options
                self._set_state(user.id, UserState.VIEWING_LUCKY_WHEEL_RESULT, preserve_current=False)
                self.user_states[user.id]["game"] = "lucky_wheel"

                breadcrumb = self._get_breadcrumb(UserState.VIEWING_LUCKY_WHEEL_RESULT)
                if result["is_win"]:
                    result_message = f"""{breadcrumb}

🎡 LUCKY WHEEL RESULT

Your bet: Number {result["selected_number"]}, R{result["stake"]:.2f}

🎲 Result: {result["drawn_number"]}

🎉 WINNER! You won R{result["payout"]:.2f}!
💰 Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
                else:
                    result_message = f"""{breadcrumb}

🎡 LUCKY WHEEL RESULT

Your bet: Number {result["selected_number"]}, R{result["stake"]:.2f}

🎲 Result: {result["drawn_number"]}

❌ Sorry, you lost!
💰 Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""

                # Send receipt immediately, then result
                await whatsapp_service.send_message(user.phone_number, receipt_message)
                return result_message

            except InvalidBetDataError as e:
                self._clear_state(user.id)
                return f"❌ Invalid bet: {str(e)}\n\nReply 'menu' to restart."
            except InvalidBetAmountError as e:
                self._clear_state(user.id)
                return f"❌ {str(e)}\n\nReply 'menu' to restart."
            except InsufficientBalanceError:
                self._clear_state(user.id)
                return "❌ Insufficient balance! Please deposit money first.\n\nReply 'menu' to restart."
            except Exception as e:
                self._clear_state(user.id)
                logger.error(f"Error in Lucky Wheel: {e}", exc_info=True)
                return f"❌ Something went wrong: {str(e)}\n\nReply 'menu' to restart."""

        return "❌ Invalid state. Please start over."

    def _show_lucky_wheel_instructions(self) -> str:
        """
        Show Lucky Wheel game instructions.

        Returns:
            Instructions message
        """
        return """🎡 LUCKY WHEEL (1-12)
Win 10x your bet!

How to play:
1. Pick a number (1-12)
2. Choose your bet amount

Format: wheel [number] [amount]
Examples:
  wheel 7 R50
  wheel 12 R20
  wheel 5 100

Min bet: R5 | Max bet: R500
Good luck! 🍀"""

    async def _handle_lucky_wheel(
        self, user: User, message: str, db: Session
    ) -> str:
        """
        Handle Lucky Wheel game betting.

        Args:
            user: User instance
            message: Message text (e.g., "wheel 7 R50")
            db: Database session

        Returns:
            Response message
        """
        # Parse message: "wheel 7 R50" or "wheel 7 50"
        # Pattern: wheel {number} {amount}
        pattern = r"wheel\s+(\d+)\s+r?(\d+(?:\.\d{1,2})?)"
        match = re.match(pattern, message.lower())

        if not match:
            return """❌ Invalid format!

Example: wheel 7 R50

🎡 LUCKY WHEEL (1-12)
Pick a number and your bet amount.

Format: wheel [number] [amount]
Example: wheel 5 R20"""

        try:
            selected_number = int(match.group(1))
            stake_amount = Decimal(match.group(2))

            # Play the game
            bet, result = await LuckyWheelGame.play(
                user_id=user.id,
                stake_amount=stake_amount,
                bet_data={"selected_number": selected_number},
                db=db,
            )

            # Get new balance
            wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
            new_balance = wallet.balance if wallet else Decimal("0.00")

            if result["is_win"]:
                return f"""🎡 LUCKY WHEEL RESULT

Your bet: Number {result["selected_number"]}, R{result["stake"]:.2f}

🎲 Result: {result["drawn_number"]}

🎉 WINNER! You won R{result["payout"]:.2f}!
💰 Balance: R{new_balance:.2f}

Play again? Send: wheel [1-12] [amount]"""
            else:
                return f"""🎡 LUCKY WHEEL RESULT

Your bet: Number {result["selected_number"]}, R{result["stake"]:.2f}

🎲 Result: {result["drawn_number"]}

❌ Sorry, you lost!
💰 Balance: R{new_balance:.2f}

Try again? Send: wheel [1-12] [amount]"""

        except InvalidBetDataError as e:
            return f"❌ Invalid bet: {str(e)}"
        except InvalidBetAmountError as e:
            return f"❌ {str(e)}"
        except InsufficientBalanceError:
            return "❌ Insufficient balance! Please deposit money first."
        except Exception as e:
            logger.error(f"Error in Lucky Wheel: {e}", exc_info=True)
            return "❌ Something went wrong. Please try again."

    async def _start_color_game_flow(self, user: User) -> str:
        """
        Start Color Game flow.

        Args:
            user: User instance

        Returns:
            Color selection prompt message
        """
        # Set new state and push current to back stack
        self._set_state(user.id, UserState.COLOR_GAME_SELECT_COLOR, preserve_current=True)
        self.user_states[user.id]["game"] = "color_game"

        breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_SELECT_COLOR)
        return f"""{breadcrumb}

🎨 COLOR GAME - Win 3x!

Pick a color:
🔴 Red (R)
🟢 Green (G)
🔵 Blue (B)
🟡 Yellow (Y)

Reply with color name or letter (e.g., 'red' or 'r'):

Reply '0' to go back."""

    async def _handle_color_game_flow(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle Color Game multi-step conversation.

        Args:
            user: User instance
            message: Message text
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        step = state.get("state")

        if step == UserState.COLOR_GAME_SELECT_COLOR:
            # User is selecting a color
            try:
                selected_color = self._validate_color(message)

                # Save to state and move to next step
                state["selected_color"] = selected_color
                state["game"] = "color_game"
                self._set_state(user.id, UserState.COLOR_GAME_ENTER_AMOUNT, preserve_current=True)

                color_emoji = ColorGame.COLOR_EMOJIS.get(selected_color, "")
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_ENTER_AMOUNT)
                return f"""{breadcrumb}

✅ Your color: {color_emoji} {selected_color.title()}

Enter bet amount (R5-R500):
Example: R30 or 50

Reply '0' or 'b' to go back."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_SELECT_COLOR)
                return f"""{breadcrumb}

❌ {str(e)}

🎨 COLOR GAME - Win 3x!

Pick a color:
🔴 Red (R)
🟢 Green (G)
🔵 Blue (B)
🟡 Yellow (Y)

Reply '0' to go back."""

        elif step == UserState.COLOR_GAME_ENTER_AMOUNT:
            # User is entering bet amount
            try:
                stake_amount = self._validate_stake(message, Decimal("5.00"), Decimal("500.00"))
                selected_color = state["selected_color"]

                # Store stake and move to confirmation
                state["stake_amount"] = stake_amount
                state["game"] = "color_game"
                self._set_state(user.id, UserState.COLOR_GAME_CONFIRM, preserve_current=True)

                # Calculate potential payout
                potential_payout = stake_amount * Decimal("3.0")
                
                # Get current balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")

                color_emoji = ColorGame.COLOR_EMOJIS.get(selected_color, "")
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_CONFIRM)
                return f"""{breadcrumb}

✅ CONFIRM YOUR BET

Game: Color Game
Your pick: {color_emoji} {selected_color.title()}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f} (3x)

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R5-R500):
Example: R30 or 50

Reply '0' or 'b' to go back."""

        elif step == UserState.COLOR_GAME_CONFIRM:
            # User is confirming or cancelling bet
            message_lower = message.lower().strip()
            
            if message_lower in ["no", "n", "cancel"]:
                # User cancelled - go back to amount entry
                state.pop("stake_amount", None)
                state["state"] = UserState.COLOR_GAME_ENTER_AMOUNT
                selected_color = state["selected_color"]
                color_emoji = ColorGame.COLOR_EMOJIS.get(selected_color, "")
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_ENTER_AMOUNT)
                return f"""{breadcrumb}

✅ Your color: {color_emoji} {selected_color.title()}

Enter bet amount (R5-R500):
Example: R30 or 50

Reply '0' or 'b' to go back."""
            
            elif message_lower not in ["yes", "y", "confirm"]:
                # Invalid confirmation response
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_CONFIRM)
                selected_color = state["selected_color"]
                stake_amount = state["stake_amount"]
                potential_payout = stake_amount * Decimal("3.0")
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                color_emoji = ColorGame.COLOR_EMOJIS.get(selected_color, "")
                return f"""{breadcrumb}

❌ Invalid response. Please reply 'yes' to confirm or 'no' to cancel.

✅ CONFIRM YOUR BET

Game: Color Game
Your pick: {color_emoji} {selected_color.title()}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f} (3x)

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""
            
            # User confirmed - place bet
            try:
                stake_amount = state["stake_amount"]
                selected_color = state["selected_color"]

                # Check balance before placing bet
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                if current_balance < stake_amount:
                    breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_CONFIRM)
                    color_emoji = ColorGame.COLOR_EMOJIS.get(selected_color, "")
                    return f"""{breadcrumb}

❌ Insufficient balance! You have R{float(current_balance):.2f}, but need R{float(stake_amount):.2f}.

Reply 'no' to cancel or 'menu' to go to main menu."""

                # Play the game
                bet, result = await ColorGame.play(
                    user_id=user.id,
                    stake_amount=stake_amount,
                    bet_data={"selected_color": selected_color},
                    db=db,
                )

                # Get new balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                new_balance = wallet.balance if wallet else Decimal("0.00")

                # Get emojis
                selected_emoji = ColorGame.COLOR_EMOJIS.get(result["selected_color"], "")
                drawn_emoji = ColorGame.COLOR_EMOJIS.get(result["drawn_color"], "")

                # Send bet receipt
                receipt_message = f"""✅ BET PLACED

Bet ID: #{bet.id}
Game: Color Game
Your pick: {selected_emoji} {selected_color.title()}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(stake_amount * Decimal("3.0")):.2f} (3x)

Round ID: #{bet.id}
Balance: R{float(new_balance):.2f}

Wait for result!"""

                # Set state to show result with options
                self._set_state(user.id, UserState.VIEWING_COLOR_GAME_RESULT, preserve_current=False)
                self.user_states[user.id]["game"] = "color_game"

                breadcrumb = self._get_breadcrumb(UserState.VIEWING_COLOR_GAME_RESULT)
                if result["is_win"]:
                    result_message = f"""{breadcrumb}

🎨 COLOR GAME RESULT

Your bet: {selected_emoji} {result["selected_color"].title()}, R{result["stake"]:.2f}

🎲 Result: {drawn_emoji} {result["drawn_color"].title()}

🎉 WINNER! You won R{result["payout"]:.2f}!
💰 Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
                else:
                    result_message = f"""{breadcrumb}

🎨 COLOR GAME RESULT

Your bet: {selected_emoji} {result["selected_color"].title()}, R{result["stake"]:.2f}

🎲 Result: {drawn_emoji} {result["drawn_color"].title()}

❌ Sorry, you lost!
💰 Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""

                # Send receipt immediately, then result
                await whatsapp_service.send_message(user.phone_number, receipt_message)
                return result_message

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R5-R500):
Example: R30 or 50

Reply '0' or 'b' to go back."""
            except InvalidBetDataError as e:
                self._clear_state(user.id)
                return f"❌ Invalid bet: {str(e)}\n\nReply 'menu' to restart."
            except InvalidBetAmountError as e:
                self._clear_state(user.id)
                return f"❌ {str(e)}\n\nReply 'menu' to restart."
            except InsufficientBalanceError:
                self._clear_state(user.id)
                return "❌ Insufficient balance! Please deposit money first.\n\nReply 'menu' to restart."
            except Exception as e:
                self._clear_state(user.id)
                logger.error(f"Error in Color Game: {e}", exc_info=True)
                return f"❌ Something went wrong: {str(e)}\n\nReply 'menu' to restart."

        return "❌ Invalid state. Please start over."

    def _show_color_game_instructions(self) -> str:
        """
        Show Color Game instructions.

        Returns:
            Instructions message
        """
        return """🎨 COLOR GAME - Win 3x!

Pick a color:
🔴 Red (R)
🟢 Green (G)
🔵 Blue (B)
🟡 Yellow (Y)

Format: color [color] [amount]
Examples:
  color red R30
  color green 50
  color b R20
  color y 100

Min bet: R5 | Max bet: R500
Good luck! 🍀"""

    async def _handle_color_game(
        self, user: User, message: str, db: Session
    ) -> str:
        """
        Handle Color Game betting.

        Args:
            user: User instance
            message: Message text (e.g., "color red R30")
            db: Database session

        Returns:
            Response message
        """
        # Parse message: "color red R30" or "color blue 50"
        pattern = r"color\s+(red|green|blue|yellow|r|g|b|y)\s+r?(\d+(?:\.\d{1,2})?)"
        match = re.match(pattern, message.lower())

        if not match:
            return """❌ Invalid format!

🎨 COLOR GAME - Win 3x!

Pick a color:
🔴 Red (R)
🟢 Green (G)
🔵 Blue (B)
🟡 Yellow (Y)

Format: color [color] [amount]
Examples:
  color red R30
  color green 50
  color b R20"""

        try:
            # Map shortcuts
            color_map = {"r": "red", "g": "green", "b": "blue", "y": "yellow"}
            color_input = match.group(1).lower()
            selected_color = color_map.get(color_input, color_input)

            stake_amount = Decimal(match.group(2))

            # Play the game
            bet, result = await ColorGame.play(
                user_id=user.id,
                stake_amount=stake_amount,
                bet_data={"selected_color": selected_color},
                db=db,
            )

            # Get new balance
            wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
            new_balance = wallet.balance if wallet else Decimal("0.00")

            # Get emojis
            selected_emoji = ColorGame.COLOR_EMOJIS.get(result["selected_color"], "")
            drawn_emoji = ColorGame.COLOR_EMOJIS.get(result["drawn_color"], "")

            if result["is_win"]:
                return f"""🎨 COLOR GAME RESULT

Your bet: {selected_emoji} {result["selected_color"].title()}, R{result["stake"]:.2f}

🎲 Result: {drawn_emoji} {result["drawn_color"].title()}

🎉 WINNER! You won R{result["payout"]:.2f}!
💰 Balance: R{new_balance:.2f}

Play again? Send: color [color] [amount]"""
            else:
                return f"""🎨 COLOR GAME RESULT

Your bet: {selected_emoji} {result["selected_color"].title()}, R{result["stake"]:.2f}

🎲 Result: {drawn_emoji} {result["drawn_color"].title()}

❌ Sorry, you lost!
💰 Balance: R{new_balance:.2f}

Try again? Send: color [color] [amount]"""

        except InvalidBetDataError as e:
            return f"❌ Invalid bet: {str(e)}"
        except InvalidBetAmountError as e:
            return f"❌ {str(e)}"
        except InsufficientBalanceError:
            return "❌ Insufficient balance! Please deposit money first."
        except Exception as e:
            logger.error(f"Error in Color Game: {e}", exc_info=True)
            return "❌ Something went wrong. Please try again."

    async def _start_pick3_flow(self, user: User) -> str:
        """
        Start Pick 3 game flow.

        Args:
            user: User instance

        Returns:
            Instructions message
        """
        # Set new state and push current to back stack
        self._set_state(user.id, UserState.PICK3_SELECT_NUMBERS, preserve_current=True)
        self.user_states[user.id]["game"] = "pick3"

        breadcrumb = self._get_breadcrumb(UserState.PICK3_SELECT_NUMBERS)
        return f"""{breadcrumb}

🎯 PICK 3 NUMBERS
Win 800x your bet!

Pick 3 numbers (1-36)
Example: 7 14 23

Send your 3 numbers:

Reply '0' or 'b' to go back."""

    async def _handle_pick3_flow(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle Pick 3 multi-step conversation.

        Args:
            user: User instance
            message: Message text
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        step = state.get("state")

        if step == UserState.PICK3_SELECT_NUMBERS:
            # User is selecting 3 numbers
            try:
                # Validate exactly 3 numbers (1-36), no duplicates
                selected_numbers = self._validate_pick3_numbers(message)

                # Additional validation using game's validate_bet_data
                selected_numbers = Pick3Game.validate_bet_data(
                    {"selected_numbers": selected_numbers}
                )

                # Save to state and move to next step
                state["selected_numbers"] = selected_numbers
                state["game"] = "pick3"
                self._set_state(user.id, UserState.PICK3_ENTER_AMOUNT, preserve_current=True)

                breadcrumb = self._get_breadcrumb(UserState.PICK3_ENTER_AMOUNT)
                return f"""{breadcrumb}

✅ Your numbers: {', '.join(map(str, selected_numbers))}

Enter bet amount (R2-R100):
Example: R10 or 50

Reply '0' or 'b' to go back."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.PICK3_SELECT_NUMBERS)
                return f"""{breadcrumb}

❌ {str(e)}

🎯 PICK 3 NUMBERS (1-36)
Example: 7 14 23

Reply '0' or 'b' to go back."""
            except Exception as e:
                breadcrumb = self._get_breadcrumb(UserState.PICK3_SELECT_NUMBERS)
                return f"""{breadcrumb}

❌ {str(e)}

🎯 PICK 3 NUMBERS (1-36)
Example: 7 14 23

Reply '0' or 'b' to go back."""

        elif step == UserState.PICK3_ENTER_AMOUNT:
            # User is entering bet amount
            try:
                stake_amount = self._validate_stake(message, Decimal("2.00"), Decimal("100.00"))
                selected_numbers = state["selected_numbers"]

                # Store stake and move to confirmation
                state["stake_amount"] = stake_amount
                state["game"] = "pick3"
                self._set_state(user.id, UserState.PICK3_CONFIRM, preserve_current=True)

                # Calculate potential payout
                potential_payout = stake_amount * Decimal("800.0")
                
                # Get current balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")

                breadcrumb = self._get_breadcrumb(UserState.PICK3_CONFIRM)
                return f"""{breadcrumb}

✅ CONFIRM YOUR BET

Game: Pick 3 Numbers
Your pick: {', '.join(map(str, selected_numbers))}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f} (800x)

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.PICK3_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R2-R100):
Example: R10 or 50

Reply '0' or 'b' to go back."""

        elif step == UserState.PICK3_CONFIRM:
            # User is confirming or cancelling bet
            message_lower = message.lower().strip()
            
            if message_lower in ["no", "n", "cancel"]:
                # User cancelled - go back to amount entry
                state.pop("stake_amount", None)
                state["state"] = UserState.PICK3_ENTER_AMOUNT
                breadcrumb = self._get_breadcrumb(UserState.PICK3_ENTER_AMOUNT)
                selected_numbers = state.get("selected_numbers", [])
                return f"""{breadcrumb}

✅ Your numbers: {', '.join(map(str, selected_numbers))}

Enter bet amount (R2-R100):
Example: R10 or 50

Reply '0' or 'b' to go back."""
            
            elif message_lower not in ["yes", "y", "confirm"]:
                # Invalid confirmation response
                breadcrumb = self._get_breadcrumb(UserState.PICK3_CONFIRM)
                selected_numbers = state["selected_numbers"]
                stake_amount = state["stake_amount"]
                potential_payout = stake_amount * Decimal("800.0")
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                return f"""{breadcrumb}

❌ Invalid response. Please reply 'yes' to confirm or 'no' to cancel.

✅ CONFIRM YOUR BET

Game: Pick 3 Numbers
Your pick: {', '.join(map(str, selected_numbers))}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f} (800x)

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""
            
            # User confirmed - place bet
            try:
                stake_amount = state["stake_amount"]
                selected_numbers = state["selected_numbers"]

                # Check balance before placing bet
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                if current_balance < stake_amount:
                    breadcrumb = self._get_breadcrumb(UserState.PICK3_CONFIRM)
                    return f"""{breadcrumb}

❌ Insufficient balance! You have R{float(current_balance):.2f}, but need R{float(stake_amount):.2f}.

Reply 'no' to cancel or 'menu' to go to main menu."""

                # Play the game
                bet, result = await Pick3Game.play(
                    user_id=user.id,
                    stake_amount=stake_amount,
                    bet_data={"selected_numbers": selected_numbers},
                    db=db,
                    enable_partial_matches=True,
                )

                # Get new balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                new_balance = wallet.balance if wallet else Decimal("0.00")

                # Send bet receipt
                receipt_message = f"""✅ BET PLACED

Bet ID: #{bet.id}
Game: Pick 3 Numbers
Your pick: {', '.join(map(str, selected_numbers))}
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(stake_amount * Decimal("800.0")):.2f} (800x)

Round ID: #{bet.id}
Balance: R{float(new_balance):.2f}

Wait for result!"""

                # Set state to show result with options
                self._set_state(user.id, UserState.VIEWING_PICK3_RESULT, preserve_current=False)
                self.user_states[user.id]["game"] = "pick3"

                # Format result message
                breadcrumb = self._get_breadcrumb(UserState.VIEWING_PICK3_RESULT)
                if result["match_count"] == 3:
                    result_message = f"""{breadcrumb}

🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

🎉🎉🎉 JACKPOT! All 3 matched!
💰 You won R{result['payout']:.2f}!

Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
                elif result["match_count"] == 2:
                    result_message = f"""{breadcrumb}

🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

✨ 2 numbers matched!
💰 You won R{result['payout']:.2f}!

Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
                elif result["match_count"] == 1:
                    result_message = f"""{breadcrumb}

🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

1 number matched!
💰 You won R{result['payout']:.2f}!

Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""
                else:
                    result_message = f"""{breadcrumb}

🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

❌ No matches - you lost!
💰 Balance: R{new_balance:.2f}

What would you like to do?

1️⃣ Play Again
2️⃣ Games Menu
0️⃣ Main Menu

Reply with number."""

                # Send receipt immediately, then result
                await whatsapp_service.send_message(user.phone_number, receipt_message)
                return result_message

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.PICK3_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R2-R100):
Example: R10 or 50

Reply '0' or 'b' to go back."""
            except InvalidBetDataError as e:
                self._clear_state(user.id)
                return f"❌ Invalid bet: {str(e)}\n\nReply 'menu' to restart."
            except InvalidBetAmountError as e:
                self._clear_state(user.id)
                return f"❌ {str(e)}\n\nReply 'menu' to restart."
            except InsufficientBalanceError:
                self._clear_state(user.id)
                return "❌ Insufficient balance! Please deposit money first.\n\nReply 'menu' to restart."
            except Exception as e:
                self._clear_state(user.id)
                logger.error(f"Error in Pick 3: {e}", exc_info=True)
                return f"❌ Error: {str(e)}\n\nReply 'menu' to restart."

        return "❌ Invalid state. Please start over."

    async def _start_football_yesno_flow(self, user: User, db: Session) -> str:
        """
        Start Football Yes/No game flow.

        Args:
            user: User instance
            db: Database session

        Returns:
            Active matches list
        """
        # Get active matches
        matches = FootballYesNoGame.get_active_matches(db, limit=10)

        if not matches:
            # Set new state and push current to back stack
            self._set_state(user.id, UserState.FOOTBALL_SELECT_MATCH, preserve_current=True)
            self.user_states[user.id]["game"] = "football"
            self.user_states[user.id]["matches"] = []  # Empty matches list
            breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
            return f"""{breadcrumb}

⚽ FOOTBALL YES/NO

No active matches available at the moment.

Check back later for new matches!

Reply '0' or 'b' to go back."""

        # Build matches list
        breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
        matches_text = f"""{breadcrumb}

⚽ FOOTBALL YES/NO

Active Matches:

"""
        for idx, match in enumerate(matches, 1):
            matches_text += f"{idx}️⃣ {match.home_team} vs {match.away_team}\n"
            matches_text += f"   {match.event_description}\n"
            matches_text += f"   YES: {float(match.yes_odds)}x | NO: {float(match.no_odds)}x\n\n"

        matches_text += "Reply with match number:"

        # Set new state and push current to back stack
        self._set_state(user.id, UserState.FOOTBALL_SELECT_MATCH, preserve_current=True)
        self.user_states[user.id]["game"] = "football"
        self.user_states[user.id]["matches"] = [
            {
                "id": m.id,
                "home_team": m.home_team,
                "away_team": m.away_team,
                "event_description": m.event_description,
                "yes_odds": float(m.yes_odds),
                "no_odds": float(m.no_odds),
            }
            for m in matches
        ]

        return matches_text + "\n\nReply '0' or 'b' to go back."

    async def _handle_football_yesno_flow(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle Football Yes/No multi-step conversation.

        Args:
            user: User instance
            message: Message text
            state: Current state
            db: Database session

        Returns:
            Response message
        """
        step = state.get("state")

        if step == UserState.FOOTBALL_SELECT_MATCH:
            # Check if there are no matches
            matches = state.get("matches", [])
            if not matches:
                # Handle back navigation when no matches
                message_lower = message.lower().strip()
                if message_lower in ["back", "0", "b"]:
                    return await self._handle_back_navigation(user, state, db)
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
                return f"""{breadcrumb}

⚽ FOOTBALL YES/NO

No active matches available at the moment.

Check back later for new matches!

Reply '0' or 'b' to go back."""
            
            # User is selecting a match
            try:
                match_num = int(message.strip())

                if match_num < 1 or match_num > len(matches):
                    breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
                    return f"""{breadcrumb}

❌ Invalid match number. Please choose 1-{len(matches)}

Reply '0' or 'b' to go back."""

                selected_match = matches[match_num - 1]

                # Update state and move to next step
                state["match_id"] = selected_match["id"]
                state["match"] = selected_match
                state["game"] = "football"
                self._set_state(user.id, UserState.FOOTBALL_SELECT_CHOICE, preserve_current=True)

                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_CHOICE)
                return f"""{breadcrumb}

⚽ {selected_match['home_team']} vs {selected_match['away_team']}
{selected_match['event_description']}

YES: {selected_match['yes_odds']}x | NO: {selected_match['no_odds']}x

Your choice (yes/no):

Reply '0' or 'b' to go back."""

            except ValueError:
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
                return f"""{breadcrumb}

❌ Invalid number. Please reply with a match number.

Reply '0' or 'b' to go back."""

        elif step == UserState.FOOTBALL_SELECT_CHOICE:
            # User is selecting Yes or No
            choice = message.lower().strip()

            if choice not in ["yes", "no", "y", "n"]:
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_CHOICE)
                return f"""{breadcrumb}

❌ Invalid choice. Please reply 'yes' or 'no'

Reply '0' or 'b' to go back."""

            # Normalize choice
            choice = "yes" if choice in ["yes", "y"] else "no"

            match_info = state["match"]
            odds = match_info["yes_odds"] if choice == "yes" else match_info["no_odds"]

            # Update state and move to next step
            state["choice"] = choice
            state["odds"] = odds
            state["game"] = "football"
            self._set_state(user.id, UserState.FOOTBALL_ENTER_AMOUNT, preserve_current=True)

            breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_ENTER_AMOUNT)
            return f"""{breadcrumb}

You chose: {choice.upper()} ({odds}x)

Enter bet amount (R10-R1000):
Example: R100 or 500

Reply '0' or 'b' to go back."""

        elif step == UserState.FOOTBALL_ENTER_AMOUNT:
            # User is entering bet amount
            try:
                stake_amount = self._validate_stake(message, Decimal("10.00"), Decimal("1000.00"))
                match_id = state["match_id"]
                choice = state["choice"]
                match_info = state["match"]
                odds = state["odds"]

                # Store stake and move to confirmation
                state["stake_amount"] = stake_amount
                state["game"] = "football"
                self._set_state(user.id, UserState.FOOTBALL_CONFIRM, preserve_current=True)

                # Calculate potential payout
                potential_payout = stake_amount * Decimal(str(odds))
                
                # Get current balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")

                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_CONFIRM)
                return f"""{breadcrumb}

✅ CONFIRM YOUR BET

Game: Football Yes/No
Match: {match_info['home_team']} vs {match_info['away_team']}
Question: {match_info['event_description']}
Your bet: {choice.upper()} ({odds}x)
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f}

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R10-R1000):
Example: R100 or 500

Reply '0' or 'b' to go back."""

        elif step == UserState.FOOTBALL_CONFIRM:
            # User is confirming or cancelling bet
            message_lower = message.lower().strip()
            
            if message_lower in ["no", "n", "cancel"]:
                # User cancelled - go back to amount entry
                state.pop("stake_amount", None)
                state["state"] = UserState.FOOTBALL_ENTER_AMOUNT
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_ENTER_AMOUNT)
                choice = state.get("choice")
                odds = state.get("odds")
                return f"""{breadcrumb}

You chose: {choice.upper()} ({odds}x)

Enter bet amount (R10-R1000):
Example: R100 or 500

Reply '0' or 'b' to go back."""
            
            elif message_lower not in ["yes", "y", "confirm"]:
                # Invalid confirmation response
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_CONFIRM)
                match_info = state["match"]
                choice = state["choice"]
                odds = state["odds"]
                stake_amount = state["stake_amount"]
                potential_payout = stake_amount * Decimal(str(odds))
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                return f"""{breadcrumb}

❌ Invalid response. Please reply 'yes' to confirm or 'no' to cancel.

✅ CONFIRM YOUR BET

Game: Football Yes/No
Match: {match_info['home_team']} vs {match_info['away_team']}
Question: {match_info['event_description']}
Your bet: {choice.upper()} ({odds}x)
Stake: R{float(stake_amount):.2f}
Potential payout: R{float(potential_payout):.2f}

Current balance: R{float(current_balance):.2f}
Balance after bet: R{float(current_balance - stake_amount):.2f}

Reply 'yes' or 'y' to confirm, 'no' or 'n' to cancel."""
            
            # User confirmed - place bet
            try:
                stake_amount = state["stake_amount"]
                match_id = state["match_id"]
                choice = state["choice"]
                match_info = state["match"]

                # Check balance before placing bet
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                current_balance = wallet.balance if wallet else Decimal("0.00")
                if current_balance < stake_amount:
                    breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_CONFIRM)
                    return f"""{breadcrumb}

❌ Insufficient balance! You have R{float(current_balance):.2f}, but need R{float(stake_amount):.2f}.

Reply 'no' to cancel or 'menu' to go to main menu."""

                # Place bet (status: pending)
                bet, result = await FootballYesNoGame.place_bet(
                    user_id=user.id,
                    stake_amount=stake_amount,
                    bet_data={"match_id": match_id, "choice": choice},
                    db=db,
                )

                # Get new balance
                wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
                new_balance = wallet.balance if wallet else Decimal("0.00")

                # Send bet receipt
                receipt_message = f"""✅ BET PLACED

Bet ID: #{bet.id}
Game: Football Yes/No
Match: {result['home_team']} vs {result['away_team']}
Question: {result['event_description']}
Your bet: {result['choice'].upper()} - R{result['stake']:.2f}
Potential payout: R{result['potential_payout']:.2f}

Round ID: #{bet.id}
Balance: R{float(new_balance):.2f}

Wait for match to end!"""

                # Clear state
                self._clear_state(user.id)

                # Send receipt immediately
                await whatsapp_service.send_message(user.phone_number, receipt_message)
                
                breadcrumb = self._get_breadcrumb()
                return f"""{breadcrumb}

✅ Bet placed!

Match: {result['home_team']} vs {result['away_team']}
Question: {result['event_description']}
Your bet: {result['choice'].upper()} - R{result['stake']:.2f}
Potential win: R{result['potential_payout']:.2f}

Wait for match to end!
💰 Balance: R{new_balance:.2f}"""

            except ValueError as e:
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_ENTER_AMOUNT)
                return f"""{breadcrumb}

❌ {str(e)}

Enter bet amount (R10-R1000):
Example: R100 or 500

Reply '0' or 'b' to go back."""
            except InvalidBetDataError as e:
                self._clear_state(user.id)
                return f"❌ Invalid bet: {str(e)}\n\nReply 'menu' to restart."
            except InvalidBetAmountError as e:
                self._clear_state(user.id)
                return f"❌ {str(e)}\n\nReply 'menu' to restart."
            except InsufficientBalanceError:
                self._clear_state(user.id)
                return "❌ Insufficient balance! Please deposit money first.\n\nReply 'menu' to restart."
            except Exception as e:
                self._clear_state(user.id)
                logger.error(f"Error in Football Yes/No: {e}", exc_info=True)
                return f"❌ Error: {str(e)}\n\nReply 'menu' to restart."

        return "❌ Invalid state. Please start over."

    async def _handle_back_navigation(
        self,
        user: User,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle back navigation - go back one step in the flow using back stack.

        Args:
            user: User instance
            state: Current user state
            db: Database session

        Returns:
            Response message
        """
        current_state = state.get("state")
        back_stack = state.get("back_stack", [])

        # If back stack is empty, go to main menu
        if not back_stack:
            self._clear_state(user.id)
            return self._show_main_menu()

        # Pop the previous state from back stack
        previous_state = self._pop_from_back_stack(user.id)
        
        if not previous_state:
            self._clear_state(user.id)
            return self._show_main_menu()

        # Handle going back based on current state
        # Restore the previous state and handle state-specific cleanup
        if current_state == UserState.AWAITING_DEPOSIT_METHOD:
            # Go back to deposit amount
            state.pop("amount", None)
            state["state"] = previous_state
            return """💰 DEPOSIT MONEY

Minimum deposit: R10
Maximum deposit: R10,000

How much would you like to deposit?
Example: 50 (for R50)

Reply '0' or 'b' to go back."""

        elif current_state == UserState.AWAITING_DEPOSIT_PROOF:
            # Go back to deposit method
            state.pop("payment_method", None)
            state.pop("method_name", None)
            state["state"] = previous_state
            amount = state.get("amount", Decimal("0.00"))
            return f"""💳 PAYMENT METHOD

Amount: R{float(amount):.2f}

Choose your payment method:

1️⃣ 1Voucher
2️⃣ SnapScan
3️⃣ Capitec
4️⃣ Bank Transfer

Reply with the number (1-4) or '0'/'b' to go back."""

        elif current_state == UserState.AWAITING_WITHDRAWAL_METHOD:
            # Go back to withdrawal amount
            state.pop("amount", None)
            state["state"] = previous_state
            try:
                balance = wallet_service.get_balance(user.id, db)
                return f"""💸 WITHDRAW MONEY

Your balance: R{float(balance):.2f}

Minimum: R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}
Maximum: R{float(withdrawal_service.MAX_WITHDRAWAL):.2f}

How much would you like to withdraw?
Example: 100 (for R100)

Reply '0' or 'b' to go back."""
            except Exception:
                return "❌ Error checking balance. Please try again later."

        elif current_state == UserState.AWAITING_WITHDRAWAL_DETAILS:
            # Go back to withdrawal method
            state.pop("withdrawal_method", None)
            state.pop("method_name", None)
            state["state"] = previous_state
            amount = state.get("amount", Decimal("0.00"))
            return f"""💳 WITHDRAWAL METHOD

Amount: R{float(amount):.2f}

Choose withdrawal method:

1️⃣ Bank Transfer (2-3 days)
2️⃣ Cash Pickup (24 hours)
3️⃣ eWallet (Instant)

Reply with the number (1-3) or '0'/'b' to go back."""

        elif current_state == UserState.PICK3_ENTER_AMOUNT:
            # Go back to pick3 number selection
            state.pop("selected_numbers", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.PICK3_SELECT_NUMBERS)
            return f"""{breadcrumb}

🎯 PICK 3 NUMBERS
Win 800x your bet!

Pick 3 numbers (1-36)
Example: 7 14 23

Send your 3 numbers:

Reply '0' or 'b' to go back."""

        elif current_state == UserState.PICK3_CONFIRM:
            # Go back to amount entry
            state.pop("stake_amount", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.PICK3_ENTER_AMOUNT)
            selected_numbers = state.get("selected_numbers", [])
            return f"""{breadcrumb}

✅ Your numbers: {', '.join(map(str, selected_numbers))}

Enter bet amount (R2-R100):
Example: R10 or 50

Reply '0' or 'b' to go back."""

        elif current_state == UserState.LUCKY_WHEEL_SELECT_NUMBER:
            # Go back from number selection
            if previous_state == UserState.VIEWING_GAMES_MENU:
                state["state"] = previous_state
                return self._show_games(user)
            else:
                self._clear_state(user.id)
                return self._show_main_menu()

        elif current_state == UserState.LUCKY_WHEEL_ENTER_AMOUNT:
            # Go back to number selection
            state.pop("selected_number", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_SELECT_NUMBER)
            return f"""{breadcrumb}

🎡 LUCKY WHEEL (1-12)
Win 10x your bet!

Select a number (1-12):

Reply '0' or 'b' to go back."""

        elif current_state == UserState.LUCKY_WHEEL_CONFIRM:
            # Go back to amount entry
            state.pop("stake_amount", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.LUCKY_WHEEL_ENTER_AMOUNT)
            selected_number = state.get("selected_number")
            return f"""{breadcrumb}

✅ Your number: {selected_number}

Enter bet amount (R5-R500):
Example: R50 or 50

Reply '0' or 'b' to go back."""

        elif current_state == UserState.COLOR_GAME_SELECT_COLOR:
            # Go back from color selection
            if previous_state == UserState.VIEWING_GAMES_MENU:
                state["state"] = previous_state
                return self._show_games(user)
            else:
                self._clear_state(user.id)
                return self._show_main_menu()

        elif current_state == UserState.COLOR_GAME_ENTER_AMOUNT:
            # Go back to color selection
            state.pop("selected_color", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_SELECT_COLOR)
            return f"""{breadcrumb}

🎨 COLOR GAME - Win 3x!

Pick a color:
🔴 Red (R)
🟢 Green (G)
🔵 Blue (B)
🟡 Yellow (Y)

Reply with color name or letter (e.g., 'red' or 'r'):

Reply '0' to go back."""

        elif current_state == UserState.COLOR_GAME_CONFIRM:
            # Go back to amount entry
            state.pop("stake_amount", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.COLOR_GAME_ENTER_AMOUNT)
            selected_color = state.get("selected_color")
            color_emoji = ColorGame.COLOR_EMOJIS.get(selected_color, "")
            return f"""{breadcrumb}

✅ Your color: {color_emoji} {selected_color.title()}

Enter bet amount (R5-R500):
Example: R30 or 50

Reply '0' or 'b' to go back."""

        elif current_state == UserState.FOOTBALL_SELECT_MATCH:
            # Go back from match selection
            if previous_state == UserState.VIEWING_GAMES_MENU:
                state["state"] = previous_state
                return self._show_games(user)
            else:
                self._clear_state(user.id)
                return self._show_main_menu()

        elif current_state == UserState.FOOTBALL_SELECT_CHOICE:
            # Go back to match selection
            state.pop("match_id", None)
            state.pop("match", None)
            state["state"] = previous_state
            # Rebuild matches list
            matches = FootballYesNoGame.get_active_matches(db, limit=10)
            if not matches:
                # Keep state so user can navigate back
                state["matches"] = []  # Empty matches list
                breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
                return f"""{breadcrumb}

⚽ FOOTBALL YES/NO

No active matches available at the moment.

Check back later for new matches!

Reply '0' or 'b' to go back."""

            breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_MATCH)
            matches_text = f"""{breadcrumb}

⚽ FOOTBALL YES/NO

Active Matches:

"""
            for idx, match in enumerate(matches, 1):
                matches_text += f"{idx}️⃣ {match.home_team} vs {match.away_team}\n"
                matches_text += f"   {match.event_description}\n"
                matches_text += f"   YES: {float(match.yes_odds)}x | NO: {float(match.no_odds)}x\n\n"

            matches_text += "Reply with match number:"

            state["matches"] = [
                {
                    "id": m.id,
                    "home_team": m.home_team,
                    "away_team": m.away_team,
                    "event_description": m.event_description,
                    "yes_odds": float(m.yes_odds),
                    "no_odds": float(m.no_odds),
                }
                for m in matches
            ]

            return matches_text + "\n\nReply '0' or 'b' to go back."

        elif current_state == UserState.FOOTBALL_ENTER_AMOUNT:
            # Go back to choice selection
            state.pop("choice", None)
            state.pop("odds", None)
            state["state"] = previous_state
            match_info = state.get("match", {})
            breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_SELECT_CHOICE)
            return f"""{breadcrumb}

⚽ {match_info.get('home_team', '')} vs {match_info.get('away_team', '')}
{match_info.get('event_description', '')}

YES: {match_info.get('yes_odds', 0)}x | NO: {match_info.get('no_odds', 0)}x

Your choice (yes/no):

Reply '0' or 'b' to go back."""

        elif current_state == UserState.FOOTBALL_CONFIRM:
            # Go back to amount entry
            state.pop("stake_amount", None)
            state["state"] = previous_state
            breadcrumb = self._get_breadcrumb(UserState.FOOTBALL_ENTER_AMOUNT)
            choice = state.get("choice")
            odds = state.get("odds")
            return f"""{breadcrumb}

You chose: {choice.upper()} ({odds}x)

Enter bet amount (R10-R1000):
Example: R100 or 500

Reply '0' or 'b' to go back."""

        elif current_state == UserState.VIEWING_GAMES_MENU:
            # Go back to main menu
            self._clear_state(user.id)
            return self._show_main_menu()

        elif current_state == UserState.VIEWING_BALANCE_MENU:
            # Go back to main menu
            self._clear_state(user.id)
            return self._show_main_menu()

        elif current_state == UserState.VIEWING_HELP_MENU:
            # Go back to main menu
            self._clear_state(user.id)
            return self._show_main_menu()

        elif current_state in [
            UserState.VIEWING_LUCKY_WHEEL_RESULT,
            UserState.VIEWING_COLOR_GAME_RESULT,
            UserState.VIEWING_PICK3_RESULT,
        ]:
            # Go back from result screen
            if previous_state:
                state["state"] = previous_state
                if previous_state == UserState.VIEWING_GAMES_MENU:
                    return self._show_games(user)
            self._clear_state(user.id)
            return self._show_main_menu()

        else:
            # Unknown state or first step - go to main menu
            self._clear_state(user.id)
            return self._show_main_menu()

    async def _handle_cancel(
        self,
        user: User,
        state: Dict[str, Any],
        db: Session,
    ) -> str:
        """
        Handle cancel command - go back one step or to main menu.

        Args:
            user: User instance
            state: Current user state
            db: Database session

        Returns:
            Response message
        """
        # Check if there's a state in back stack
        back_stack = state.get("back_stack", [])
        if back_stack:
            return await self._handle_back_navigation(user, state, db)

        # Otherwise, go to main menu
        self._clear_state(user.id)
        return self._show_main_menu()


# Singleton instance
message_router = MessageRouter()
