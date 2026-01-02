# Phase 3 Implementation Plan
## WhatsApp Betting Platform MVP - Game Engines & Betting Logic

**Version:** 1.0
**Date:** January 2026
**Duration:** Week 3-4 (10 days)
**Goal:** Implement 4 game engines (Lucky Wheel, Color Game, Pick 3, Football Yes/No) with complete betting logic, win/loss calculation, and WhatsApp integration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 3 Objectives](#phase-3-objectives)
3. [Success Criteria](#success-criteria)
4. [Prerequisites](#prerequisites)
5. [Game Specifications](#game-specifications)
6. [Day 1: Bet Model & Core Betting Service](#day-1-bet-model--core-betting-service)
7. [Day 2-3: Lucky Wheel Game Engine](#day-2-3-lucky-wheel-game-engine)
8. [Day 4-5: Color Game Engine](#day-4-5-color-game-engine)
9. [Day 6-7: Pick 3 Numbers Game Engine](#day-6-7-pick-3-numbers-game-engine)
10. [Day 8-9: Football Yes/No Game Engine](#day-8-9-football-yesno-game-engine)
11. [Day 10: Integration Testing & Optimization](#day-10-integration-testing--optimization)
12. [Deliverables Checklist](#deliverables-checklist)
13. [Testing Strategy](#testing-strategy)
14. [Troubleshooting Guide](#troubleshooting-guide)
15. [Next Steps](#next-steps)

---

## Executive Summary

Phase 3 builds upon the foundation established in Phases 1 and 2 by implementing the core gaming functionality of the platform. This phase focuses on:

- **Game Engines**: Four distinct game types with unique mechanics and payout structures
- **Betting System**: Robust bet placement, validation, and settlement logic
- **Win/Loss Calculation**: Accurate payout calculation with proper financial handling
- **WhatsApp Integration**: Seamless game interaction through WhatsApp messages
- **Game State Management**: Multi-step conversation flows for complex betting interactions
- **Random Number Generation**: Cryptographically secure RNG for fair game outcomes

By the end of Phase 3, the system will be able to:
- Allow users to place bets on 4 different games via WhatsApp
- Generate fair and random game outcomes
- Calculate winnings accurately based on game-specific multipliers
- Settle bets automatically (debit stake, credit winnings)
- Maintain complete audit trail of all bets and outcomes
- Handle concurrent betting from multiple users
- Provide game history and statistics to users
- Prevent common betting bugs (double betting, negative stakes, race conditions)

---

## Phase 3 Objectives

### Primary Objectives

1. ✅ **Bet Management System**
   - Create bet database model with all required fields
   - Implement bet placement service with validation
   - Add bet settlement logic (win/loss processing)
   - Create bet history and statistics queries
   - Implement bet cancellation and refund logic

2. ✅ **Lucky Wheel Game (1-12)**
   - Implement wheel spin mechanics
   - Add bet placement flow via WhatsApp
   - Create random number generation (1-12)
   - Implement 10x payout calculation
   - Add game result notification

3. ✅ **Color Game**
   - Implement color selection mechanics (Red, Green, Blue, Yellow)
   - Add multi-step betting flow
   - Create fair color selection algorithm
   - Implement 3x payout for correct color
   - Add instant play mode

4. ✅ **Pick 3 Numbers Game**
   - Implement 3-number selection (range 1-36)
   - Add number validation (no duplicates)
   - Create draw mechanics with 3 random numbers
   - Implement 800x payout for exact match
   - Add partial match rewards (optional)

5. ✅ **Football Yes/No Game**
   - Implement match selection interface
   - Add Yes/No bet placement
   - Create odds calculation system
   - Implement variable payout based on odds
   - Add match result settlement
   - Create admin interface for match management

### Secondary Objectives

- Implement bet limits (minimum/maximum stakes)
- Add responsible gambling features (daily limits)
- Create leaderboard system
- Implement game statistics dashboard
- Add anti-fraud detection
- Create automated game scheduling
- Implement push notifications for game results
- Add game result verification system

---

## Success Criteria

Phase 3 is considered complete when:

### Functional Requirements

- [ ] Users can place bets on all 4 games via WhatsApp
- [ ] Lucky Wheel game generates random numbers (1-12) and pays 10x
- [ ] Color Game allows color selection and pays 3x for correct color
- [ ] Pick 3 game validates 3 unique numbers and pays 800x for exact match
- [ ] Football Yes/No game supports match betting with variable odds
- [ ] All bets are deducted from wallet immediately on placement
- [ ] All winnings are credited to wallet immediately on settlement
- [ ] Users can view bet history via WhatsApp
- [ ] Game results are announced clearly with winnings breakdown
- [ ] All financial transactions are atomic (no partial settlements)
- [ ] Concurrent bets from different users work correctly
- [ ] Invalid bets are rejected with clear error messages
- [ ] All game outcomes are provably fair and random

### Technical Requirements

- [ ] Bet model includes all necessary audit fields
- [ ] All game engines use cryptographically secure RNG
- [ ] Bet placement uses database transactions (ACID compliance)
- [ ] Win/loss calculations use Decimal type (no floating point errors)
- [ ] Game state is properly managed for multi-step flows
- [ ] All amounts are validated before processing
- [ ] Wallet operations use the WalletService from Phase 2
- [ ] Code follows Python best practices with type hints
- [ ] Error handling covers all edge cases
- [ ] Logging captures all game events for audit

### Testing Requirements

- [ ] Unit tests for each game engine
- [ ] Integration tests for bet placement flows
- [ ] Win/loss calculation accuracy tests
- [ ] Concurrent betting stress tests
- [ ] Balance integrity tests after multiple bets
- [ ] Invalid input handling tests
- [ ] Edge case tests (zero balance, maximum stakes, etc.)
- [ ] End-to-end tests for complete game flows

---

## Prerequisites

Before starting Phase 3, ensure:

- [ ] Phase 1 is fully complete and tested
- [ ] Phase 2 is fully complete and tested
- [ ] FastAPI server is running without errors
- [ ] PostgreSQL database is accessible
- [ ] WalletService is working correctly
- [ ] Users can register and check balance
- [ ] Deposit/withdrawal flows are functional
- [ ] WhatsApp webhook is receiving and responding to messages
- [ ] Message router supports state management
- [ ] All Phase 1 and Phase 2 tests are passing

### Required Tools

- Python 3.10+ with FastAPI
- PostgreSQL 14+
- Redis 6+ (for game state management)
- SQLAlchemy 2.0+
- pytest for testing
- Python secrets module for secure RNG

### Knowledge Prerequisites

- Understanding of database transactions
- Familiarity with the WalletService API
- Knowledge of the MessageRouter state system
- Understanding of Decimal arithmetic for financial calculations

---

## Game Specifications

### Game 1: Lucky Wheel (1-12)

**Concept:** User bets on a number from 1-12. A random number is drawn. If it matches, user wins.

**Mechanics:**
- User selects a number between 1 and 12
- Minimum bet: R5
- Maximum bet: R500
- Single step betting (user sends: "wheel 7 R20")
- Random number generated using cryptographically secure RNG
- Win condition: User's number matches drawn number
- Payout: 10x stake (e.g., R20 bet wins R200)
- Loss: Stake is lost
- House edge: ~16.67% ((12-10)/12)

**WhatsApp Flow:**
```
User: "2" (from games menu - select Lucky Wheel)
Bot: "🎡 LUCKY WHEEL (1-12)
     Win 10x your bet!

     Pick a number: 1-12
     Example: wheel 7 R20"

User: "wheel 5 R50"
Bot: "🎡 Spinning the wheel...

     Your bet: Number 5, R50

     🎲 Result: 5

     🎉 WINNER! You won R500!
     💰 Balance: R550 → R1,000"

User: "wheel 3 R20"
Bot: "🎡 Spinning the wheel...

     Your bet: Number 3, R20

     🎲 Result: 8

     ❌ Sorry, you lost!
     💰 Balance: R1,000 → R980"
```

**Database Fields:**
- bet_type: "lucky_wheel"
- bet_data: `{"selected_number": 5}`
- game_result: `{"drawn_number": 5}`
- multiplier: 10.0
- payout_amount: stake * 10 (if win), 0 (if loss)

---

### Game 2: Color Game

**Concept:** User bets on a color (Red, Green, Blue, Yellow). A random color is drawn. If it matches, user wins.

**Mechanics:**
- User selects one of 4 colors: Red (R), Green (G), Blue (B), Yellow (Y)
- Minimum bet: R5
- Maximum bet: R500
- Single step betting (user sends: "color red R30")
- Random color generated using cryptographically secure RNG
- Win condition: User's color matches drawn color
- Payout: 3x stake (e.g., R30 bet wins R90)
- Loss: Stake is lost
- House edge: 25% ((4-3)/4)

**WhatsApp Flow:**
```
User: "2" (from games menu - select Color Game)
Bot: "🎨 COLOR GAME
     Win 3x your bet!

     Pick a color:
     🔴 Red (R)
     🟢 Green (G)
     🔵 Blue (B)
     🟡 Yellow (Y)

     Example: color red R30"

User: "color green R100"
Bot: "🎨 Drawing color...

     Your bet: 🟢 Green, R100

     🎲 Result: 🟢 Green

     🎉 WINNER! You won R300!
     💰 Balance: R400 → R600"

User: "color blue R50"
Bot: "🎨 Drawing color...

     Your bet: 🔵 Blue, R50

     🎲 Result: 🔴 Red

     ❌ Sorry, you lost!
     💰 Balance: R600 → R550"
```

**Database Fields:**
- bet_type: "color_game"
- bet_data: `{"selected_color": "green"}`
- game_result: `{"drawn_color": "green"}`
- multiplier: 3.0
- payout_amount: stake * 3 (if win), 0 (if loss)

---

### Game 3: Pick 3 Numbers

**Concept:** User picks 3 unique numbers from 1-36. System draws 3 random numbers. If all 3 match (any order), user wins.

**Mechanics:**
- User selects 3 unique numbers between 1 and 36
- Numbers must be unique (no duplicates allowed)
- Minimum bet: R2
- Maximum bet: R100
- Multi-step betting flow
- Random 3 numbers generated using cryptographically secure RNG
- Win condition: All 3 user numbers match drawn numbers (any order)
- Payout: 800x stake (e.g., R10 bet wins R8,000)
- Loss: Stake is lost
- House edge: ~98.3% (extremely low win probability, high payout)
- Optional: Partial matches (2 numbers = 10x, 1 number = 2x)

**WhatsApp Flow:**
```
User: "3" (from games menu - select Pick 3)
Bot: "🎯 PICK 3 NUMBERS
     Win 800x your bet!

     Pick 3 numbers (1-36)
     Example: 7 14 23

     Send your 3 numbers:"

User: "5 12 28"
Bot: "Your numbers: 5, 12, 28

     Enter bet amount (R2-R100):"

User: "R10"
Bot: "🎯 Drawing numbers...

     Your bet: 5, 12, 28 - R10

     🎲 Result: 5, 12, 28

     🎉 JACKPOT! All 3 matched!
     💰 You won R8,000!
     Balance: R100 → R8,090"

User: "8 15 22"
Bot: "Your numbers: 8, 15, 22

     Enter bet amount (R2-R100):"

User: "R5"
Bot: "🎯 Drawing numbers...

     Your bet: 8, 15, 22 - R5

     🎲 Result: 3, 15, 31

     ❌ No match - you lost!
     💰 Balance: R8,090 → R8,085"
```

**Database Fields:**
- bet_type: "pick_3"
- bet_data: `{"selected_numbers": [5, 12, 28]}`
- game_result: `{"drawn_numbers": [5, 12, 28], "match_count": 3}`
- multiplier: 800.0 (3 matches), 10.0 (2 matches), 2.0 (1 match), 0 (no match)
- payout_amount: stake * multiplier

**Win Probability:**
- 3 matches: 1 in 7,140 (0.014%)
- 2 matches: ~4.7%
- 1 match: ~29.8%

---

### Game 4: Football Yes/No

**Concept:** Admin creates football matches with Yes/No betting options. Users bet Yes or No on match outcomes. Variable odds based on match.

**Mechanics:**
- Admin creates matches with: teams, event, yes_odds, no_odds
- User selects Yes or No for a specific match
- Minimum bet: R10
- Maximum bet: R1000
- Odds vary per match (e.g., Yes: 1.5x, No: 2.3x)
- Admin settles match as Yes or No after real match ends
- Win condition: User's choice matches admin settlement
- Payout: stake * odds
- Loss: Stake is lost

**WhatsApp Flow:**
```
User: "4" (from games menu - select Football Yes/No)
Bot: "⚽ FOOTBALL YES/NO

     Active Matches:

     1️⃣ Chiefs vs Pirates
        Will Chiefs score first?
        YES: 1.8x | NO: 2.1x

     2️⃣ Sundowns vs Cosmos
        Over 2.5 goals?
        YES: 1.5x | NO: 2.5x

     Reply with match number:"

User: "1"
Bot: "⚽ Chiefs vs Pirates
     Will Chiefs score first?

     YES: 1.8x | NO: 2.1x

     Your choice (yes/no):"

User: "yes"
Bot: "You chose: YES (1.8x)

     Enter bet amount (R10-R1000):"

User: "R100"
Bot: "✅ Bet placed!

     Match: Chiefs vs Pirates
     Question: Will Chiefs score first?
     Your bet: YES - R100
     Potential win: R180

     Wait for match to end!
     💰 Balance: R500 → R400"

[After admin settles match as "yes"]
Bot: "⚽ MATCH SETTLED

     Chiefs vs Pirates
     Result: YES ✅

     Your bet: YES - R100
     🎉 You won R180!
     💰 Balance: R400 → R580"
```

**Database Fields:**
- bet_type: "football_yesno"
- bet_data: `{"match_id": 1, "choice": "yes"}`
- game_result: `{"match_result": "yes"}` (set by admin)
- multiplier: 1.8 (yes_odds) or 2.1 (no_odds)
- payout_amount: stake * multiplier (if win), 0 (if loss)
- status: "pending" → "settled"

**Additional Table: Matches**
- id, home_team, away_team, event_description
- yes_odds, no_odds
- status: "active", "settled", "cancelled"
- result: "yes", "no", null
- created_at, settled_at

---

## Day 1: Bet Model & Core Betting Service

**Duration:** 6-8 hours
**Goal:** Create bet database model, implement core betting service with atomic operations, and set up bet history queries

### Prerequisites

- Phase 2 WalletService is working
- Database connection is stable
- Transaction model exists from Phase 2

### Step 1: Create Bet Model (1.5 hours)

#### 1.1 Create app/models/bet.py

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from decimal import Decimal
from enum import Enum
from ..database import Base


class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class BetType(str, Enum):
    LUCKY_WHEEL = "lucky_wheel"
    COLOR_GAME = "color_game"
    PICK_3 = "pick_3"
    FOOTBALL_YESNO = "football_yesno"


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Bet details
    bet_type = Column(SQLEnum(BetType), nullable=False, index=True)
    stake_amount = Column(Numeric(10, 2), nullable=False)

    # Bet data (JSON string with bet-specific data)
    # Example: {"selected_number": 5} for lucky_wheel
    # Example: {"selected_color": "red"} for color_game
    # Example: {"selected_numbers": [5, 12, 28]} for pick_3
    # Example: {"match_id": 1, "choice": "yes"} for football_yesno
    bet_data = Column(String(500), nullable=False)

    # Game result (JSON string with result data)
    # Example: {"drawn_number": 5} for lucky_wheel
    # Example: {"drawn_color": "red"} for color_game
    # Example: {"drawn_numbers": [3, 15, 31], "match_count": 1} for pick_3
    # Example: {"match_result": "yes"} for football_yesno
    game_result = Column(String(500), nullable=True)

    # Outcome
    status = Column(SQLEnum(BetStatus), default=BetStatus.PENDING, nullable=False, index=True)
    multiplier = Column(Numeric(10, 2), nullable=True)  # Payout multiplier (e.g., 10.0 for lucky_wheel)
    payout_amount = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)  # Actual payout (stake * multiplier)

    # Metadata
    ip_address = Column(String(50), nullable=True)  # For fraud detection
    user_agent = Column(String(200), nullable=True)  # For fraud detection

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)  # When bet was settled (won/lost)

    # Relationships
    user = relationship("User", back_populates="bets")

    # Composite indexes for efficient queries
    __table_args__ = (
        Index('ix_user_created', 'user_id', 'created_at'),
        Index('ix_user_type', 'user_id', 'bet_type'),
        Index('ix_status_created', 'status', 'created_at'),
    )

    def __repr__(self):
        return f"<Bet(id={self.id}, user_id={self.user_id}, type={self.bet_type}, stake={self.stake_amount}, status={self.status})>"
```

#### 1.2 Create app/models/match.py (for Football Yes/No game)

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, Enum as SQLEnum
from decimal import Decimal
from enum import Enum
from ..database import Base


class MatchStatus(str, Enum):
    ACTIVE = "active"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class MatchResult(str, Enum):
    YES = "yes"
    NO = "no"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    # Match details
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    event_description = Column(String(200), nullable=False)  # "Will Chiefs score first?"

    # Odds
    yes_odds = Column(Numeric(5, 2), nullable=False)  # e.g., 1.80
    no_odds = Column(Numeric(5, 2), nullable=False)  # e.g., 2.10

    # Status and result
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.ACTIVE, nullable=False, index=True)
    result = Column(SQLEnum(MatchResult), nullable=True)  # Set by admin when settling

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    match_time = Column(DateTime(timezone=True), nullable=True)  # Scheduled match time
    settled_at = Column(DateTime(timezone=True), nullable=True)  # When admin settled the match

    def __repr__(self):
        return f"<Match(id={self.id}, {self.home_team} vs {self.away_team}, status={self.status})>"
```

#### 1.3 Update User Model Relationships

Add to `app/models/user.py`:

```python
# Add this to the User class relationships section
bets = relationship("Bet", back_populates="user", cascade="all, delete-orphan")
```

#### 1.4 Update app/models/__init__.py

```python
from .user import User
from .wallet import Wallet, Transaction
from .bet import Bet, BetStatus, BetType
from .match import Match, MatchStatus, MatchResult

__all__ = [
    "User",
    "Wallet",
    "Transaction",
    "Bet",
    "BetStatus",
    "BetType",
    "Match",
    "MatchStatus",
    "MatchResult"
]
```

#### 1.5 Initialize Database Tables

Run database initialization to create new tables:

```python
# Update app/database.py to import new models
from app.models import User, Wallet, Transaction, Bet, Match  # noqa: F401
```

Then run:

```bash
python -c "from app.database import init_db; init_db()"
```

Or restart your FastAPI server (it will auto-create tables on startup).

### Step 2: Create Core Betting Service (3 hours)

#### 2.1 Create app/services/bet_service.py

```python
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import datetime
import logging
import json

from ..models.user import User
from ..models.bet import Bet, BetStatus, BetType
from ..models.wallet import Transaction
from ..services.wallet_service import WalletService, InsufficientBalanceError
from ..database import get_db

logger = logging.getLogger(__name__)


class BettingError(Exception):
    """Base exception for betting errors"""
    pass


class InvalidBetAmountError(BettingError):
    """Raised when bet amount is invalid"""
    pass


class InvalidBetDataError(BettingError):
    """Raised when bet data is invalid"""
    pass


class BetService:
    """
    Service for handling all betting operations

    All bet placements and settlements MUST use this service
    to ensure proper financial handling and audit trails.
    """

    # Bet limits per game (min, max)
    BET_LIMITS = {
        BetType.LUCKY_WHEEL: (Decimal('5.00'), Decimal('500.00')),
        BetType.COLOR_GAME: (Decimal('5.00'), Decimal('500.00')),
        BetType.PICK_3: (Decimal('2.00'), Decimal('100.00')),
        BetType.FOOTBALL_YESNO: (Decimal('10.00'), Decimal('1000.00')),
    }

    @staticmethod
    def place_bet(
        user_id: int,
        bet_type: BetType,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Bet:
        """
        Place a bet for a user

        This operation:
        1. Validates bet amount is within limits
        2. Validates user has sufficient balance
        3. Creates bet record
        4. Debits stake from wallet (atomic transaction)

        Args:
            user_id: User ID
            bet_type: Type of bet (lucky_wheel, color_game, etc.)
            stake_amount: Amount to bet
            bet_data: Bet-specific data as dict
            db: Database session
            ip_address: User's IP address (for fraud detection)
            user_agent: User's user agent (for fraud detection)

        Returns:
            Created Bet object

        Raises:
            InvalidBetAmountError: If stake is invalid
            InsufficientBalanceError: If user has insufficient balance
        """
        try:
            # Validate bet amount
            min_bet, max_bet = BetService.BET_LIMITS.get(bet_type, (Decimal('1.00'), Decimal('10000.00')))

            if stake_amount < min_bet:
                raise InvalidBetAmountError(f"Minimum bet for {bet_type} is R{min_bet}")

            if stake_amount > max_bet:
                raise InvalidBetAmountError(f"Maximum bet for {bet_type} is R{max_bet}")

            # Create bet record (status=PENDING)
            bet = Bet(
                user_id=user_id,
                bet_type=bet_type,
                stake_amount=stake_amount,
                bet_data=json.dumps(bet_data),
                status=BetStatus.PENDING,
                ip_address=ip_address,
                user_agent=user_agent
            )

            db.add(bet)
            db.flush()  # Get bet.id before committing

            # Debit stake from wallet (this will raise InsufficientBalanceError if not enough balance)
            WalletService.debit(
                user_id=user_id,
                amount=stake_amount,
                transaction_type="bet",
                description=f"Bet placed: {bet_type} (Bet #{bet.id})",
                db=db,
                reference_type="bet",
                reference_id=bet.id,
                metadata=bet_data
            )

            # Commit transaction (bet + wallet debit are atomic)
            db.commit()
            db.refresh(bet)

            logger.info(
                f"Bet placed: user_id={user_id}, bet_id={bet.id}, "
                f"type={bet_type}, stake={stake_amount}"
            )

            return bet

        except InsufficientBalanceError:
            db.rollback()
            raise
        except InvalidBetAmountError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error placing bet: {e}", exc_info=True)
            raise BettingError(f"Failed to place bet: {str(e)}")

    @staticmethod
    def settle_bet(
        bet_id: int,
        game_result: Dict[str, Any],
        is_win: bool,
        multiplier: Decimal,
        db: Session
    ) -> Bet:
        """
        Settle a bet (mark as won or lost)

        This operation:
        1. Updates bet record with game result
        2. If win: credits payout to wallet
        3. Marks bet as settled

        Args:
            bet_id: Bet ID to settle
            game_result: Game result data as dict
            is_win: Whether the bet won
            multiplier: Payout multiplier (e.g., 10.0 for lucky_wheel)
            db: Database session

        Returns:
            Updated Bet object

        Raises:
            BettingError: If bet cannot be settled
        """
        try:
            # Get bet with row lock
            bet = db.query(Bet).filter(
                Bet.id == bet_id
            ).with_for_update().first()

            if not bet:
                raise BettingError(f"Bet {bet_id} not found")

            if bet.status != BetStatus.PENDING:
                raise BettingError(f"Bet {bet_id} is already settled (status: {bet.status})")

            # Update bet record
            bet.game_result = json.dumps(game_result)
            bet.multiplier = multiplier
            bet.settled_at = func.now()

            if is_win:
                # Calculate payout
                payout = bet.stake_amount * multiplier
                bet.payout_amount = payout
                bet.status = BetStatus.WON

                # Credit payout to wallet
                WalletService.credit(
                    user_id=bet.user_id,
                    amount=payout,
                    transaction_type="win",
                    description=f"Bet won: {bet.bet_type} (Bet #{bet.id})",
                    db=db,
                    reference_type="bet",
                    reference_id=bet.id,
                    metadata=game_result
                )

                logger.info(
                    f"Bet won: bet_id={bet.id}, user_id={bet.user_id}, "
                    f"stake={bet.stake_amount}, payout={payout}, multiplier={multiplier}"
                )
            else:
                # Bet lost - no payout
                bet.payout_amount = Decimal('0.00')
                bet.status = BetStatus.LOST

                logger.info(
                    f"Bet lost: bet_id={bet.id}, user_id={bet.user_id}, "
                    f"stake={bet.stake_amount}"
                )

            # Commit transaction
            db.commit()
            db.refresh(bet)

            return bet

        except BettingError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error settling bet: {e}", exc_info=True)
            raise BettingError(f"Failed to settle bet: {str(e)}")

    @staticmethod
    def refund_bet(
        bet_id: int,
        reason: str,
        db: Session
    ) -> Bet:
        """
        Refund a bet (return stake to user)

        This operation:
        1. Marks bet as refunded
        2. Credits stake back to wallet

        Args:
            bet_id: Bet ID to refund
            reason: Reason for refund
            db: Database session

        Returns:
            Updated Bet object
        """
        try:
            # Get bet with row lock
            bet = db.query(Bet).filter(
                Bet.id == bet_id
            ).with_for_update().first()

            if not bet:
                raise BettingError(f"Bet {bet_id} not found")

            if bet.status != BetStatus.PENDING:
                raise BettingError(f"Can only refund pending bets (current status: {bet.status})")

            # Update bet status
            bet.status = BetStatus.REFUNDED
            bet.settled_at = func.now()
            bet.game_result = json.dumps({"refund_reason": reason})

            # Credit stake back to wallet
            WalletService.credit(
                user_id=bet.user_id,
                amount=bet.stake_amount,
                transaction_type="refund",
                description=f"Bet refunded: {reason} (Bet #{bet.id})",
                db=db,
                reference_type="bet",
                reference_id=bet.id,
                metadata={"refund_reason": reason}
            )

            logger.info(
                f"Bet refunded: bet_id={bet.id}, user_id={bet.user_id}, "
                f"stake={bet.stake_amount}, reason={reason}"
            )

            db.commit()
            db.refresh(bet)

            return bet

        except BettingError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error refunding bet: {e}", exc_info=True)
            raise BettingError(f"Failed to refund bet: {str(e)}")

    @staticmethod
    def get_bet_history(
        user_id: int,
        db: Session,
        limit: int = 10,
        offset: int = 0,
        bet_type: Optional[BetType] = None,
        status: Optional[BetStatus] = None
    ) -> List[Bet]:
        """
        Get bet history for a user

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of bets to return
            offset: Number of bets to skip
            bet_type: Filter by bet type (optional)
            status: Filter by status (optional)

        Returns:
            List of Bet objects, ordered by created_at desc
        """
        query = db.query(Bet).filter(Bet.user_id == user_id)

        if bet_type:
            query = query.filter(Bet.bet_type == bet_type)

        if status:
            query = query.filter(Bet.status == status)

        bets = query.order_by(
            desc(Bet.created_at)
        ).limit(limit).offset(offset).all()

        return bets

    @staticmethod
    def get_bet_statistics(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get betting statistics for a user

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Dict with statistics
        """
        # Total bets
        total_bets = db.query(func.count(Bet.id)).filter(
            Bet.user_id == user_id
        ).scalar()

        # Total wagered
        total_wagered = db.query(func.sum(Bet.stake_amount)).filter(
            Bet.user_id == user_id
        ).scalar() or Decimal('0.00')

        # Total won
        total_won = db.query(func.sum(Bet.payout_amount)).filter(
            and_(Bet.user_id == user_id, Bet.status == BetStatus.WON)
        ).scalar() or Decimal('0.00')

        # Win count
        win_count = db.query(func.count(Bet.id)).filter(
            and_(Bet.user_id == user_id, Bet.status == BetStatus.WON)
        ).scalar()

        # Loss count
        loss_count = db.query(func.count(Bet.id)).filter(
            and_(Bet.user_id == user_id, Bet.status == BetStatus.LOST)
        ).scalar()

        # Win rate
        win_rate = (win_count / total_bets * 100) if total_bets > 0 else 0

        # Net profit/loss
        net_profit = total_won - total_wagered

        return {
            "total_bets": total_bets,
            "total_wagered": float(total_wagered),
            "total_won": float(total_won),
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": round(win_rate, 2),
            "net_profit": float(net_profit)
        }
```

### Step 3: Test Betting Service (1.5 hours)

#### 3.1 Create test_bet_service.py

```python
"""Test betting service"""
from decimal import Decimal
from app.database import SessionLocal, init_db
from app.models import User, Wallet, Bet, BetType, BetStatus
from app.services.bet_service import BetService, InvalidBetAmountError


def test_place_bet():
    """Test placing a bet"""
    db = SessionLocal()
    try:
        # Create test user with wallet
        user = User(phone_number="27821111111")
        db.add(user)
        db.flush()

        wallet = Wallet(user_id=user.id, balance=Decimal('1000.00'))
        db.add(wallet)
        db.commit()
        db.refresh(user)

        # Place bet
        bet = BetService.place_bet(
            user_id=user.id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=Decimal('50.00'),
            bet_data={"selected_number": 7},
            db=db
        )

        print(f"✅ Bet placed: ID {bet.id}, Stake: R{bet.stake_amount}")

        # Verify wallet debited
        db.refresh(wallet)
        assert wallet.balance == Decimal('950.00'), f"Expected R950, got R{wallet.balance}"
        print(f"✅ Wallet debited correctly: R{wallet.balance}")

        # Settle bet as win
        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result={"drawn_number": 7},
            is_win=True,
            multiplier=Decimal('10.0'),
            db=db
        )

        print(f"✅ Bet settled as WIN: Payout R{bet.payout_amount}")

        # Verify wallet credited
        db.refresh(wallet)
        expected_balance = Decimal('950.00') + Decimal('500.00')  # 950 + (50 * 10)
        assert wallet.balance == expected_balance, f"Expected R{expected_balance}, got R{wallet.balance}"
        print(f"✅ Wallet credited correctly: R{wallet.balance}")

        # Cleanup
        db.delete(user)
        db.commit()

        print("\n✅ All betting service tests passed!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nTesting betting service...")
    test_place_bet()
```

#### 3.2 Run Test

```bash
python test_bet_service.py
```

**Expected output:**
```
Initializing database...
Database tables initialized successfully

Testing betting service...
✅ Bet placed: ID 1, Stake: R50.00
✅ Wallet debited correctly: R950.00
✅ Bet settled as WIN: Payout R500.00
✅ Wallet credited correctly: R1450.00

✅ All betting service tests passed!
```

### Day 1 Deliverables

By end of Day 1, you should have:

- [x] Bet model created with all required fields
- [x] Match model created for Football Yes/No game
- [x] Database tables created (bets, matches)
- [x] BetService implemented with place_bet, settle_bet, refund_bet
- [x] Bet history and statistics queries implemented
- [x] Unit tests for betting service passing
- [x] All financial operations atomic and safe

### Day 1 Checklist

- [ ] Bet model created in app/models/bet.py
- [ ] Match model created in app/models/match.py
- [ ] User model updated with bets relationship
- [ ] Database tables created successfully
- [ ] BetService class created with all methods
- [ ] place_bet method works correctly
- [ ] settle_bet method works correctly
- [ ] refund_bet method works correctly
- [ ] Bet limits enforced
- [ ] Wallet integration working
- [ ] Test script created and passing
- [ ] All operations are atomic (ACID compliant)

---

## Day 2-3: Lucky Wheel Game Engine

**Duration:** 12-16 hours (2 days)
**Goal:** Implement complete Lucky Wheel game with bet placement, random number generation, and result settlement

### Overview

Lucky Wheel is the simplest game - user picks a number (1-12), system draws a random number, if they match, user wins 10x their stake.

### Step 1: Create Lucky Wheel Game Service (Day 2 - 6 hours)

#### 1.1 Create app/services/games/lucky_wheel.py

```python
import secrets
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from ...models.bet import Bet, BetType
from ...services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class LuckyWheelGame:
    """Lucky Wheel game engine - pick a number 1-12, win 10x"""
    
    MULTIPLIER = Decimal('10.0')
    MIN_NUMBER = 1
    MAX_NUMBER = 12
    
    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any]) -> int:
        """
        Validate bet data for Lucky Wheel
        
        Args:
            bet_data: Dict with 'selected_number' key
            
        Returns:
            Selected number (1-12)
            
        Raises:
            InvalidBetDataError: If data is invalid
        """
        if 'selected_number' not in bet_data:
            raise InvalidBetDataError("Missing 'selected_number' in bet data")
        
        selected_number = bet_data['selected_number']
        
        if not isinstance(selected_number, int):
            raise InvalidBetDataError(f"Selected number must be an integer, got {type(selected_number)}")
        
        if selected_number < LuckyWheelGame.MIN_NUMBER or selected_number > LuckyWheelGame.MAX_NUMBER:
            raise InvalidBetDataError(
                f"Number must be between {LuckyWheelGame.MIN_NUMBER} and {LuckyWheelGame.MAX_NUMBER}"
            )
        
        return selected_number
    
    @staticmethod
    def generate_result() -> int:
        """
        Generate random number (1-12) using cryptographically secure RNG
        
        Returns:
            Random number between 1 and 12 (inclusive)
        """
        return secrets.randbelow(12) + 1  # 0-11 -> 1-12
    
    @staticmethod
    def check_win(selected_number: int, drawn_number: int) -> bool:
        """
        Check if user won
        
        Args:
            selected_number: User's selected number
            drawn_number: Drawn number
            
        Returns:
            True if win, False otherwise
        """
        return selected_number == drawn_number
    
    @staticmethod
    async def play(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session
    ) -> Tuple[Bet, Dict[str, Any]]:
        """
        Play Lucky Wheel game
        
        This method:
        1. Validates bet data
        2. Places bet (debits wallet)
        3. Generates random result
        4. Determines win/loss
        5. Settles bet (credits winnings if won)
        
        Args:
            user_id: User ID
            stake_amount: Bet amount
            bet_data: {"selected_number": 5}
            db: Database session
            
        Returns:
            Tuple of (Bet object, result dict for WhatsApp message)
        """
        # Validate bet data
        selected_number = LuckyWheelGame.validate_bet_data(bet_data)
        
        # Place bet (debit stake from wallet)
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=stake_amount,
            bet_data=bet_data,
            db=db
        )
        
        # Generate result
        drawn_number = LuckyWheelGame.generate_result()
        
        # Check if win
        is_win = LuckyWheelGame.check_win(selected_number, drawn_number)
        
        # Settle bet
        game_result = {"drawn_number": drawn_number}
        multiplier = LuckyWheelGame.MULTIPLIER if is_win else Decimal('0.0')
        
        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result=game_result,
            is_win=is_win,
            multiplier=multiplier,
            db=db
        )
        
        # Prepare result for WhatsApp
        result = {
            "selected_number": selected_number,
            "drawn_number": drawn_number,
            "is_win": is_win,
            "stake": float(stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(multiplier)
        }
        
        logger.info(
            f"Lucky Wheel played: user_id={user_id}, bet_id={bet.id}, "
            f"selected={selected_number}, drawn={drawn_number}, win={is_win}"
        )
        
        return bet, result
```

### Step 2: Integrate with Message Router (Day 2 - 3 hours)

#### 2.1 Update app/services/message_router.py

Add Lucky Wheel handler to MessageRouter class:

```python
from decimal import Decimal
import re
from .games.lucky_wheel import LuckyWheelGame
from ..models.bet import BetType

# Add to MessageRouter class:

async def _handle_lucky_wheel(
    self,
    user: User,
    message: str,
    db: Session
) -> str:
    """Handle Lucky Wheel game betting"""
    
    # Parse message: "wheel 7 R50" or "wheel 7 50"
    # Pattern: wheel {number} {amount}
    pattern = r'wheel\s+(\d+)\s+r?(\d+(?:\.\d{1,2})?)'
    match = re.match(pattern, message)
    
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
            db=db
        )
        
        # Get new balance
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
        new_balance = wallet.balance if wallet else Decimal('0.00')
        
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
    except InsufficientBalanceError:
        return "❌ Insufficient balance! Please deposit money first."
    except Exception as e:
        logger.error(f"Error in Lucky Wheel: {e}", exc_info=True)
        return "❌ Something went wrong. Please try again."

# Update _handle_main_menu to add Lucky Wheel command
# Add to command mappings:
commands = {
    ...
    'wheel': lambda: self._show_lucky_wheel_instructions(),
    ...
}

def _show_lucky_wheel_instructions(self) -> str:
    """Show Lucky Wheel game instructions"""
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
```

#### 2.2 Update game menu in _show_games()

```python
async def _show_games(self) -> str:
    """Show available games"""
    return """🎮 CHOOSE YOUR GAME:

1️⃣ Lucky Wheel (1-12) - Win 10x
   Send: wheel [1-12] [amount]
   Example: wheel 7 R50

2️⃣ Color Game - Win 3x
3️⃣ Pick 3 Numbers - Win 800x
4️⃣ Football Yes/No - Various odds

Reply 'wheel' for Lucky Wheel instructions."""
```

### Step 3: Testing (Day 3 - 3-4 hours)

#### 3.1 Create test_lucky_wheel.py

```python
"""Test Lucky Wheel game"""
import asyncio
from decimal import Decimal
from app.database import SessionLocal, init_db
from app.models import User, Wallet
from app.services.games.lucky_wheel import LuckyWheelGame


async def test_lucky_wheel():
    """Test Lucky Wheel game flow"""
    db = SessionLocal()
    try:
        # Create test user
        user = User(phone_number="27829999999")
        db.add(user)
        db.flush()
        
        wallet = Wallet(user_id=user.id, balance=Decimal('1000.00'))
        db.add(wallet)
        db.commit()
        db.refresh(user)
        
        print("✅ Test user created with R1000 balance")
        
        # Test valid bet
        bet, result = await LuckyWheelGame.play(
            user_id=user.id,
            stake_amount=Decimal('50.00'),
            bet_data={"selected_number": 7},
            db=db
        )
        
        print(f"✅ Bet placed: ID {bet.id}")
        print(f"   Selected: {result['selected_number']}, Drawn: {result['drawn_number']}")
        print(f"   Result: {'WIN' if result['is_win'] else 'LOSS'}")
        print(f"   Payout: R{result['payout']:.2f}")
        
        # Verify balance
        db.refresh(wallet)
        print(f"   Balance after: R{wallet.balance:.2f}")
        
        # Test invalid number
        try:
            LuckyWheelGame.validate_bet_data({"selected_number": 13})
            print("❌ Should have raised error for number > 12")
        except Exception:
            print("✅ Correctly rejected number > 12")
        
        # Cleanup
        db.delete(user)
        db.commit()
        
        print("\n✅ All Lucky Wheel tests passed!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nTesting Lucky Wheel game...")
    asyncio.run(test_lucky_wheel())
```

### Day 2-3 Deliverables

By end of Day 3, you should have:

- [x] LuckyWheelGame service implemented
- [x] Cryptographically secure RNG for number generation
- [x] Bet validation and placement working
- [x] Win/loss calculation accurate
- [x] WhatsApp message handler integrated
- [x] Unit tests passing
- [x] End-to-end game flow working

### Day 2-3 Checklist

- [ ] Lucky Wheel game service created
- [ ] Random number generator uses secrets module
- [ ] Bet validation enforces 1-12 range
- [ ] Game correctly identifies wins/losses
- [ ] 10x multiplier applied on wins
- [ ] Message router handles "wheel" command
- [ ] WhatsApp response messages are clear
- [ ] Test script created and passing
- [ ] Users can play via WhatsApp

---

## Day 4-5: Color Game Engine

**Duration:** 12-16 hours (2 days)
**Goal:** Implement Color Game with 4 color options, random color generation, and 3x payout

### Overview

Color Game allows users to bet on one of 4 colors (Red, Green, Blue, Yellow). If the drawn color matches, user wins 3x their stake.

### Step 1: Create Color Game Service (Day 4 - 6 hours)

#### 1.1 Create app/services/games/color_game.py

```python
import secrets
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from enum import Enum

from ...models.bet import Bet, BetType
from ...services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"


class ColorGame:
    """Color Game engine - pick a color, win 3x"""
    
    MULTIPLIER = Decimal('3.0')
    VALID_COLORS = ["red", "green", "blue", "yellow"]
    
    COLOR_EMOJIS = {
        "red": "🔴",
        "green": "🟢",
        "blue": "🔵",
        "yellow": "🟡"
    }
    
    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any]) -> str:
        """Validate bet data for Color Game"""
        if 'selected_color' not in bet_data:
            raise InvalidBetDataError("Missing 'selected_color' in bet data")
        
        selected_color = bet_data['selected_color'].lower()
        
        if selected_color not in ColorGame.VALID_COLORS:
            raise InvalidBetDataError(
                f"Invalid color. Must be one of: {', '.join(ColorGame.VALID_COLORS)}"
            )
        
        return selected_color
    
    @staticmethod
    def generate_result() -> str:
        """Generate random color using cryptographically secure RNG"""
        index = secrets.randbelow(4)  # 0-3
        return ColorGame.VALID_COLORS[index]
    
    @staticmethod
    def check_win(selected_color: str, drawn_color: str) -> bool:
        """Check if user won"""
        return selected_color.lower() == drawn_color.lower()
    
    @staticmethod
    async def play(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session
    ) -> Tuple[Bet, Dict[str, Any]]:
        """Play Color Game"""
        # Validate bet data
        selected_color = ColorGame.validate_bet_data(bet_data)
        
        # Place bet
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.COLOR_GAME,
            stake_amount=stake_amount,
            bet_data={"selected_color": selected_color},
            db=db
        )
        
        # Generate result
        drawn_color = ColorGame.generate_result()
        
        # Check if win
        is_win = ColorGame.check_win(selected_color, drawn_color)
        
        # Settle bet
        game_result = {"drawn_color": drawn_color}
        multiplier = ColorGame.MULTIPLIER if is_win else Decimal('0.0')
        
        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result=game_result,
            is_win=is_win,
            multiplier=multiplier,
            db=db
        )
        
        # Prepare result
        result = {
            "selected_color": selected_color,
            "drawn_color": drawn_color,
            "is_win": is_win,
            "stake": float(stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(multiplier)
        }
        
        logger.info(
            f"Color Game played: user_id={user_id}, bet_id={bet.id}, "
            f"selected={selected_color}, drawn={drawn_color}, win={is_win}"
        )
        
        return bet, result
```

### Step 2: Integrate with Message Router (Day 4 - 3 hours)

Add to MessageRouter:

```python
async def _handle_color_game(
    self,
    user: User,
    message: str,
    db: Session
) -> str:
    """Handle Color Game betting"""
    
    # Parse message: "color red R30" or "color blue 50"
    pattern = r'color\s+(red|green|blue|yellow|r|g|b|y)\s+r?(\d+(?:\.\d{1,2})?)'
    match = re.match(pattern, message)
    
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
        from .games.color_game import ColorGame
        bet, result = await ColorGame.play(
            user_id=user.id,
            stake_amount=stake_amount,
            bet_data={"selected_color": selected_color},
            db=db
        )
        
        # Get new balance
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
        new_balance = wallet.balance if wallet else Decimal('0.00')
        
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
    except InsufficientBalanceError:
        return "❌ Insufficient balance! Please deposit money first."
    except Exception as e:
        logger.error(f"Error in Color Game: {e}", exc_info=True)
        return "❌ Something went wrong. Please try again."
```

### Step 3: Testing (Day 5 - 3-4 hours)

Create comprehensive tests for Color Game including edge cases, color validation, and payout calculations.

### Day 4-5 Deliverables

- [x] ColorGame service implemented
- [x] 4-color random generation working
- [x] 3x payout calculation accurate
- [x] WhatsApp integration complete
- [x] Color emoji support
- [x] Tests passing

---

## Day 6-7: Pick 3 Numbers Game Engine

**Duration:** 12-16 hours (2 days)
**Goal:** Implement Pick 3 game with multi-step conversation flow, number validation, and 800x jackpot

### Overview

Pick 3 is the most complex game - users pick 3 unique numbers (1-36), system draws 3 random numbers, and checks for matches with optional partial match payouts.

### Step 1: Create Pick 3 Game Service (Day 6 - 7 hours)

#### 1.1 Create app/services/games/pick_3.py

```python
import secrets
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple, List, Set
from sqlalchemy.orm import Session

from ...models.bet import Bet, BetType
from ...services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class Pick3Game:
    """Pick 3 Numbers game - pick 3 unique numbers (1-36), win 800x for exact match"""
    
    JACKPOT_MULTIPLIER = Decimal('800.0')  # All 3 match
    TWO_MATCH_MULTIPLIER = Decimal('10.0')  # 2 numbers match (optional)
    ONE_MATCH_MULTIPLIER = Decimal('2.0')   # 1 number matches (optional)
    
    MIN_NUMBER = 1
    MAX_NUMBER = 36
    NUMBERS_TO_PICK = 3
    
    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any]) -> List[int]:
        """Validate bet data for Pick 3"""
        if 'selected_numbers' not in bet_data:
            raise InvalidBetDataError("Missing 'selected_numbers' in bet data")
        
        selected_numbers = bet_data['selected_numbers']
        
        if not isinstance(selected_numbers, list):
            raise InvalidBetDataError("'selected_numbers' must be a list")
        
        if len(selected_numbers) != Pick3Game.NUMBERS_TO_PICK:
            raise InvalidBetDataError(
                f"Must select exactly {Pick3Game.NUMBERS_TO_PICK} numbers"
            )
        
        # Check all are integers
        if not all(isinstance(n, int) for n in selected_numbers):
            raise InvalidBetDataError("All numbers must be integers")
        
        # Check range
        for num in selected_numbers:
            if num < Pick3Game.MIN_NUMBER or num > Pick3Game.MAX_NUMBER:
                raise InvalidBetDataError(
                    f"Numbers must be between {Pick3Game.MIN_NUMBER} and {Pick3Game.MAX_NUMBER}"
                )
        
        # Check uniqueness
        if len(selected_numbers) != len(set(selected_numbers)):
            raise InvalidBetDataError("Numbers must be unique (no duplicates)")
        
        return sorted(selected_numbers)
    
    @staticmethod
    def generate_result() -> List[int]:
        """
        Generate 3 unique random numbers (1-36) using cryptographically secure RNG
        
        Returns:
            List of 3 unique random numbers, sorted
        """
        numbers: Set[int] = set()
        
        while len(numbers) < Pick3Game.NUMBERS_TO_PICK:
            num = secrets.randbelow(Pick3Game.MAX_NUMBER) + 1  # 1-36
            numbers.add(num)
        
        return sorted(list(numbers))
    
    @staticmethod
    def check_matches(selected_numbers: List[int], drawn_numbers: List[int]) -> int:
        """
        Check how many numbers match
        
        Args:
            selected_numbers: User's selected numbers (sorted)
            drawn_numbers: Drawn numbers (sorted)
            
        Returns:
            Number of matches (0-3)
        """
        selected_set = set(selected_numbers)
        drawn_set = set(drawn_numbers)
        
        return len(selected_set.intersection(drawn_set))
    
    @staticmethod
    def get_multiplier(match_count: int, enable_partial_matches: bool = True) -> Decimal:
        """
        Get payout multiplier based on match count
        
        Args:
            match_count: Number of matching numbers (0-3)
            enable_partial_matches: Whether to pay for partial matches
            
        Returns:
            Multiplier (Decimal)
        """
        if match_count == 3:
            return Pick3Game.JACKPOT_MULTIPLIER
        elif match_count == 2 and enable_partial_matches:
            return Pick3Game.TWO_MATCH_MULTIPLIER
        elif match_count == 1 and enable_partial_matches:
            return Pick3Game.ONE_MATCH_MULTIPLIER
        else:
            return Decimal('0.0')
    
    @staticmethod
    async def play(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
        enable_partial_matches: bool = True
    ) -> Tuple[Bet, Dict[str, Any]]:
        """Play Pick 3 game"""
        # Validate bet data
        selected_numbers = Pick3Game.validate_bet_data(bet_data)
        
        # Place bet
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.PICK_3,
            stake_amount=stake_amount,
            bet_data={"selected_numbers": selected_numbers},
            db=db
        )
        
        # Generate result
        drawn_numbers = Pick3Game.generate_result()
        
        # Check matches
        match_count = Pick3Game.check_matches(selected_numbers, drawn_numbers)
        is_win = match_count > 0 if enable_partial_matches else match_count == 3
        
        # Get multiplier
        multiplier = Pick3Game.get_multiplier(match_count, enable_partial_matches)
        
        # Settle bet
        game_result = {
            "drawn_numbers": drawn_numbers,
            "match_count": match_count
        }
        
        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result=game_result,
            is_win=is_win,
            multiplier=multiplier,
            db=db
        )
        
        # Prepare result
        result = {
            "selected_numbers": selected_numbers,
            "drawn_numbers": drawn_numbers,
            "match_count": match_count,
            "is_win": is_win,
            "stake": float(stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(multiplier)
        }
        
        logger.info(
            f"Pick 3 played: user_id={user_id}, bet_id={bet.id}, "
            f"selected={selected_numbers}, drawn={drawn_numbers}, matches={match_count}"
        )
        
        return bet, result
```

### Step 2: Multi-Step Conversation Flow (Day 6 - 4 hours)

Update MessageRouter to handle multi-step Pick 3 flow:

```python
# Add to MessageRouter class:

async def _handle_pick3_flow(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle Pick 3 multi-step conversation"""
    
    step = state.get('step', 'select_numbers')
    
    if step == 'select_numbers':
        # User is selecting 3 numbers
        # Parse: "5 12 28" or "7, 14, 23"
        numbers = re.findall(r'\d+', message)
        
        if len(numbers) != 3:
            return """❌ Please select exactly 3 numbers!

🎯 PICK 3 NUMBERS (1-36)
Example: 7 14 23"""
        
        try:
            selected_numbers = [int(n) for n in numbers]
            
            # Validate
            from .games.pick_3 import Pick3Game
            selected_numbers = Pick3Game.validate_bet_data(
                {"selected_numbers": selected_numbers}
            )
            
            # Save to state
            self.user_states[user.id] = {
                'game': 'pick3',
                'step': 'enter_amount',
                'selected_numbers': selected_numbers
            }
            
            return f"""✅ Your numbers: {', '.join(map(str, selected_numbers))}

Enter bet amount (R2-R100):
Example: R10 or 50"""
            
        except Exception as e:
            return f"❌ {str(e)}\n\nPlease try again."
    
    elif step == 'enter_amount':
        # User is entering bet amount
        amount_match = re.search(r'r?(\d+(?:\.\d{1,2})?)', message)
        
        if not amount_match:
            return "❌ Invalid amount. Example: R10 or 50"
        
        try:
            stake_amount = Decimal(amount_match.group(1))
            selected_numbers = state['selected_numbers']
            
            # Play the game
            from .games.pick_3 import Pick3Game
            bet, result = await Pick3Game.play(
                user_id=user.id,
                stake_amount=stake_amount,
                bet_data={"selected_numbers": selected_numbers},
                db=db,
                enable_partial_matches=True
            )
            
            # Clear state
            self.user_states.pop(user.id, None)
            
            # Get new balance
            wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
            new_balance = wallet.balance if wallet else Decimal('0.00')
            
            # Format result message
            if result["match_count"] == 3:
                return f"""🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

🎉🎉🎉 JACKPOT! All 3 matched!
💰 You won R{result['payout']:.2f}!

Balance: R{new_balance:.2f}"""
            elif result["match_count"] == 2:
                return f"""🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

✨ 2 numbers matched!
💰 You won R{result['payout']:.2f}!

Balance: R{new_balance:.2f}"""
            elif result["match_count"] == 1:
                return f"""🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

1 number matched!
💰 You won R{result['payout']:.2f}!

Balance: R{new_balance:.2f}"""
            else:
                return f"""🎯 PICK 3 RESULT

Your numbers: {', '.join(map(str, result['selected_numbers']))}
Drawn: {', '.join(map(str, result['drawn_numbers']))}

❌ No matches - you lost!
💰 Balance: R{new_balance:.2f}

Try again? Reply with 3 numbers."""
        
        except Exception as e:
            self.user_states.pop(user.id, None)
            logger.error(f"Error in Pick 3: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"
```

### Step 3: Testing (Day 7 - 3-5 hours)

Comprehensive testing including:
- Number validation (range, uniqueness, count)
- Match counting logic
- Partial match payouts
- Multi-step conversation flow
- Edge cases

### Day 6-7 Deliverables

- [x] Pick3Game service with jackpot logic
- [x] Partial match rewards (2 numbers = 10x, 1 number = 2x)
- [x] Multi-step conversation flow
- [x] Number validation (1-36, unique, count=3)
- [x] Tests passing

---

## Day 8-9: Football Yes/No Game Engine

**Duration:** 12-16 hours (2 days)
**Goal:** Implement Football Yes/No game with admin-managed matches, variable odds, and manual settlement

### Overview

Football Yes/No is unique - admins create matches with Yes/No questions and odds. Users bet on outcomes. Admins settle matches after real-world events conclude.

### Step 1: Create Football Match Service (Day 8 - 5 hours)

#### 1.1 Create app/services/games/football_yesno.py

```python
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ...models.bet import Bet, BetType
from ...models.match import Match, MatchStatus, MatchResult
from ...services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class FootballYesNoGame:
    """Football Yes/No game - bet on match outcomes with variable odds"""
    
    @staticmethod
    def create_match(
        home_team: str,
        away_team: str,
        event_description: str,
        yes_odds: Decimal,
        no_odds: Decimal,
        match_time: Optional[datetime],
        db: Session
    ) -> Match:
        """
        Create a new match (admin only)
        
        Args:
            home_team: Home team name
            away_team: Away team name
            event_description: Question/event (e.g., "Will Chiefs score first?")
            yes_odds: Odds for YES bet (e.g., 1.80)
            no_odds: Odds for NO bet (e.g., 2.10)
            match_time: Scheduled match time
            db: Database session
            
        Returns:
            Created Match object
        """
        match = Match(
            home_team=home_team,
            away_team=away_team,
            event_description=event_description,
            yes_odds=yes_odds,
            no_odds=no_odds,
            match_time=match_time,
            status=MatchStatus.ACTIVE
        )
        
        db.add(match)
        db.commit()
        db.refresh(match)
        
        logger.info(
            f"Match created: {home_team} vs {away_team}, "
            f"event='{event_description}', yes_odds={yes_odds}, no_odds={no_odds}"
        )
        
        return match
    
    @staticmethod
    def get_active_matches(db: Session, limit: int = 10) -> List[Match]:
        """Get all active matches"""
        return db.query(Match).filter(
            Match.status == MatchStatus.ACTIVE
        ).order_by(Match.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any], db: Session) -> Tuple[int, str, Decimal]:
        """
        Validate bet data for Football Yes/No
        
        Args:
            bet_data: {"match_id": 1, "choice": "yes"}
            db: Database session
            
        Returns:
            Tuple of (match_id, choice, odds)
            
        Raises:
            InvalidBetDataError: If data is invalid
        """
        if 'match_id' not in bet_data:
            raise InvalidBetDataError("Missing 'match_id' in bet data")
        
        if 'choice' not in bet_data:
            raise InvalidBetDataError("Missing 'choice' in bet data")
        
        match_id = bet_data['match_id']
        choice = bet_data['choice'].lower()
        
        if choice not in ['yes', 'no']:
            raise InvalidBetDataError("Choice must be 'yes' or 'no'")
        
        # Get match
        match = db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            raise InvalidBetDataError(f"Match {match_id} not found")
        
        if match.status != MatchStatus.ACTIVE:
            raise InvalidBetDataError(f"Match is {match.status}, betting closed")
        
        # Get odds
        odds = match.yes_odds if choice == 'yes' else match.no_odds
        
        return match_id, choice, odds
    
    @staticmethod
    async def place_bet(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session
    ) -> Tuple[Bet, Dict[str, Any]]:
        """
        Place a Football Yes/No bet
        
        Note: This does NOT settle the bet immediately.
        Bets remain PENDING until admin settles the match.
        """
        # Validate bet data
        match_id, choice, odds = FootballYesNoGame.validate_bet_data(bet_data, db)
        
        # Get match details
        match = db.query(Match).filter(Match.id == match_id).first()
        
        # Place bet (status will be PENDING)
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.FOOTBALL_YESNO,
            stake_amount=stake_amount,
            bet_data={
                "match_id": match_id,
                "choice": choice,
                "odds": float(odds)
            },
            db=db
        )
        
        # Prepare result (bet is pending, not settled yet)
        result = {
            "match_id": match_id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "event_description": match.event_description,
            "choice": choice,
            "odds": float(odds),
            "stake": float(stake_amount),
            "potential_payout": float(stake_amount * odds),
            "status": "pending"
        }
        
        logger.info(
            f"Football bet placed: user_id={user_id}, bet_id={bet.id}, "
            f"match_id={match_id}, choice={choice}, odds={odds}"
        )
        
        return bet, result
    
    @staticmethod
    def settle_match(
        match_id: int,
        result: MatchResult,
        db: Session
    ) -> List[Bet]:
        """
        Settle a match and all associated bets (admin only)
        
        Args:
            match_id: Match ID to settle
            result: Match result (YES or NO)
            db: Database session
            
        Returns:
            List of settled Bet objects
        """
        # Get match
        match = db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        if match.status != MatchStatus.ACTIVE:
            raise ValueError(f"Match is already {match.status}")
        
        # Update match
        match.result = result
        match.status = MatchStatus.SETTLED
        match.settled_at = datetime.utcnow()
        
        # Get all pending bets for this match
        from ...models.bet import BetStatus
        import json
        
        pending_bets = db.query(Bet).filter(
            Bet.bet_type == BetType.FOOTBALL_YESNO,
            Bet.status == BetStatus.PENDING
        ).all()
        
        settled_bets = []
        
        for bet in pending_bets:
            bet_data = json.loads(bet.bet_data)
            
            # Check if this bet is for this match
            if bet_data.get('match_id') != match_id:
                continue
            
            # Check if bet won
            user_choice = bet_data.get('choice')
            is_win = (user_choice == result.value)
            
            # Get odds
            odds = Decimal(str(bet_data.get('odds', 0)))
            multiplier = odds if is_win else Decimal('0.0')
            
            # Settle bet
            game_result = {
                "match_result": result.value,
                "match_id": match_id
            }
            
            settled_bet = BetService.settle_bet(
                bet_id=bet.id,
                game_result=game_result,
                is_win=is_win,
                multiplier=multiplier,
                db=db
            )
            
            settled_bets.append(settled_bet)
        
        db.commit()
        
        logger.info(
            f"Match settled: match_id={match_id}, result={result.value}, "
            f"settled_bets={len(settled_bets)}"
        )
        
        return settled_bets
```

### Step 2: Admin API Endpoints (Day 8 - 3 hours)

#### 2.1 Create app/api/admin.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional, List

from ..database import get_db
from ..services.games.football_yesno import FootballYesNoGame
from ..models.match import Match, MatchStatus, MatchResult

router = APIRouter()


class CreateMatchRequest(BaseModel):
    home_team: str
    away_team: str
    event_description: str
    yes_odds: Decimal
    no_odds: Decimal
    match_time: Optional[datetime] = None


class SettleMatchRequest(BaseModel):
    result: str  # "yes" or "no"


@router.post("/matches", response_model=dict)
async def create_match(
    request: CreateMatchRequest,
    db: Session = Depends(get_db)
):
    """Create a new football match (admin only)"""
    try:
        match = FootballYesNoGame.create_match(
            home_team=request.home_team,
            away_team=request.away_team,
            event_description=request.event_description,
            yes_odds=request.yes_odds,
            no_odds=request.no_odds,
            match_time=request.match_time,
            db=db
        )
        
        return {
            "success": True,
            "match_id": match.id,
            "message": "Match created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/matches", response_model=List[dict])
async def get_matches(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all matches"""
    query = db.query(Match)
    
    if status:
        query = query.filter(Match.status == status)
    
    matches = query.order_by(Match.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": m.id,
            "home_team": m.home_team,
            "away_team": m.away_team,
            "event_description": m.event_description,
            "yes_odds": float(m.yes_odds),
            "no_odds": float(m.no_odds),
            "status": m.status,
            "result": m.result if m.result else None,
            "created_at": m.created_at.isoformat(),
            "settled_at": m.settled_at.isoformat() if m.settled_at else None
        }
        for m in matches
    ]


@router.post("/matches/{match_id}/settle", response_model=dict)
async def settle_match(
    match_id: int,
    request: SettleMatchRequest,
    db: Session = Depends(get_db)
):
    """Settle a match (admin only)"""
    try:
        result = MatchResult.YES if request.result.lower() == "yes" else MatchResult.NO
        
        settled_bets = FootballYesNoGame.settle_match(
            match_id=match_id,
            result=result,
            db=db
        )
        
        return {
            "success": True,
            "match_id": match_id,
            "result": result.value,
            "settled_bets": len(settled_bets),
            "message": f"Match settled as {result.value.upper()}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 2.2 Update app/main.py

```python
from .api import admin

# Include admin router
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
```

### Step 3: WhatsApp Integration (Day 9 - 4-5 hours)

Add Football Yes/No handlers to MessageRouter with multi-step flow for match selection and bet placement.

### Step 4: Testing (Day 9 - 3-4 hours)

Test complete flow:
1. Admin creates matches via API
2. Users see active matches via WhatsApp
3. Users place bets
4. Admin settles matches
5. Bets are automatically settled
6. Winnings credited to wallets

### Day 8-9 Deliverables

- [x] FootballYesNoGame service
- [x] Match creation/management
- [x] Variable odds support
- [x] Admin API endpoints
- [x] Batch bet settlement
- [x] WhatsApp integration
- [x] Tests passing

---

## Day 10: Integration Testing & Optimization

**Duration:** 6-8 hours
**Goal:** Comprehensive testing, bug fixes, performance optimization, and final validation

### Step 1: End-to-End Testing (3 hours)

#### 1.1 Create comprehensive test suite

Test all games:
- Lucky Wheel: Single-step betting
- Color Game: Color selection and payouts
- Pick 3: Multi-step flow and jackpot
- Football Yes/No: Match creation, betting, settlement

#### 1.2 Test concurrent betting

Ensure no race conditions when multiple users bet simultaneously.

#### 1.3 Test edge cases

- Zero balance
- Maximum stakes
- Invalid inputs
- Duplicate bets
- Database connection failures

### Step 2: Performance Optimization (2 hours)

#### 2.1 Database query optimization

Add indexes:
```sql
CREATE INDEX idx_bets_user_status ON bets(user_id, status);
CREATE INDEX idx_bets_created_at ON bets(created_at DESC);
CREATE INDEX idx_matches_status ON matches(status);
```

#### 2.2 Add Redis caching (optional)

Cache active matches and user balances for faster lookups.

### Step 3: Final Validation (2-3 hours)

#### 3.1 Balance integrity checks

Verify all wallet balances match transaction history:

```python
def verify_all_balances(db: Session):
    """Verify all user balances match transaction history"""
    users = db.query(User).all()
    
    for user in users:
        wallet_balance = WalletService.get_balance(user.id, db)
        is_valid = WalletService.verify_balance_integrity(user.id, db)
        
        if not is_valid:
            logger.error(f"Balance mismatch for user {user.id}")
        else:
            logger.info(f"✅ User {user.id} balance verified: R{wallet_balance}")
```

#### 3.2 Payout calculation verification

Manually verify payout calculations for each game:
- Lucky Wheel: 10x
- Color Game: 3x
- Pick 3: 800x / 10x / 2x
- Football: Variable odds

#### 3.3 Load testing

Simulate 50-100 concurrent users placing bets.

### Day 10 Deliverables

- [x] All games tested end-to-end
- [x] Concurrent betting works correctly
- [x] No balance integrity issues
- [x] Performance optimized
- [x] All edge cases handled
- [x] Documentation updated

---

## Deliverables Checklist

### Code Deliverables

#### Models
- [x] Bet model with all fields and enums
- [x] Match model for Football Yes/No
- [x] Database relationships configured
- [x] Indexes optimized for queries

#### Services
- [x] BetService (place, settle, refund, history, statistics)
- [x] LuckyWheelGame engine
- [x] ColorGame engine
- [x] Pick3Game engine
- [x] FootballYesNoGame engine
- [x] Match management service

#### API Endpoints
- [x] Admin endpoints for match management
- [x] Match creation endpoint
- [x] Match settlement endpoint
- [x] Match listing endpoint

#### WhatsApp Integration
- [x] Lucky Wheel command handler
- [x] Color Game command handler
- [x] Pick 3 multi-step flow
- [x] Football Yes/No multi-step flow
- [x] Game menu updated
- [x] Help commands updated

#### Testing
- [x] Unit tests for each game engine
- [x] Integration tests for bet placement
- [x] End-to-end game flow tests
- [x] Concurrent betting tests
- [x] Balance integrity tests
- [x] Edge case tests

---

## Testing Strategy

### Unit Testing

Test each component in isolation:

```python
# Example unit test structure
class TestLuckyWheel:
    def test_validate_bet_data_valid(self):
        """Test valid bet data passes validation"""
        bet_data = {"selected_number": 7}
        result = LuckyWheelGame.validate_bet_data(bet_data)
        assert result == 7
    
    def test_validate_bet_data_invalid_range(self):
        """Test number out of range fails validation"""
        bet_data = {"selected_number": 13}
        with pytest.raises(InvalidBetDataError):
            LuckyWheelGame.validate_bet_data(bet_data)
    
    def test_generate_result_in_range(self):
        """Test generated numbers are in valid range"""
        for _ in range(100):
            result = LuckyWheelGame.generate_result()
            assert 1 <= result <= 12
```

### Integration Testing

Test component interactions:

```python
async def test_full_lucky_wheel_flow():
    """Test complete Lucky Wheel game flow"""
    db = SessionLocal()
    
    # Create user with balance
    user = User(phone_number="27821111111")
    db.add(user)
    db.flush()
    
    wallet = Wallet(user_id=user.id, balance=Decimal('100.00'))
    db.add(wallet)
    db.commit()
    
    # Play game
    bet, result = await LuckyWheelGame.play(
        user_id=user.id,
        stake_amount=Decimal('10.00'),
        bet_data={"selected_number": 5},
        db=db
    )
    
    # Verify bet created
    assert bet.id is not None
    assert bet.bet_type == BetType.LUCKY_WHEEL
    
    # Verify wallet debited
    db.refresh(wallet)
    if result["is_win"]:
        # Won: stake debited, payout credited
        assert wallet.balance == Decimal('100.00') - Decimal('10.00') + Decimal('100.00')
    else:
        # Lost: only stake debited
        assert wallet.balance == Decimal('90.00')
    
    db.delete(user)
    db.commit()
```

### Performance Testing

Test system under load:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def simulate_concurrent_bets(num_users: int = 50):
    """Simulate concurrent betting from multiple users"""
    
    async def place_random_bet(user_id: int):
        db = SessionLocal()
        try:
            # Random game and stake
            stake = Decimal('10.00')
            bet_data = {"selected_number": secrets.randbelow(12) + 1}
            
            bet, result = await LuckyWheelGame.play(
                user_id=user_id,
                stake_amount=stake,
                bet_data=bet_data,
                db=db
            )
            
            return result
        finally:
            db.close()
    
    # Create tasks for concurrent bets
    tasks = [place_random_bet(i) for i in range(1, num_users + 1)]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"Placed {num_users} bets in {end_time - start_time:.2f} seconds")
    print(f"Average: {(end_time - start_time) / num_users * 1000:.2f}ms per bet")
```

---

## Troubleshooting Guide

### Common Issues

#### Issue: Race condition in concurrent betting

**Symptoms:** Multiple bets processed simultaneously, wallet balance becomes negative

**Solution:** Ensure `with_for_update()` is used in WalletService:
```python
wallet = db.query(Wallet).filter(
    Wallet.user_id == user_id
).with_for_update().first()
```

#### Issue: Floating point errors in payout calculations

**Symptoms:** Payouts like R99.99999999 instead of R100.00

**Solution:** Always use `Decimal` type, never `float`:
```python
# Wrong
payout = stake * 10.0

# Correct
payout = stake * Decimal('10.0')
```

#### Issue: Bets not settling for Football Yes/No

**Symptoms:** Bets remain PENDING after match settlement

**Solution:** Ensure bet_data contains correct match_id:
```python
import json
bet_data = json.loads(bet.bet_data)
if bet_data.get('match_id') == match_id:
    # Settle bet
```

#### Issue: Pick 3 numbers not being validated correctly

**Symptoms:** Duplicate numbers accepted, numbers outside 1-36 accepted

**Solution:** Validate before placing bet:
```python
if len(set(numbers)) != len(numbers):
    raise InvalidBetDataError("Duplicates not allowed")

if any(n < 1 or n > 36 for n in numbers):
    raise InvalidBetDataError("Numbers must be 1-36")
```

#### Issue: WhatsApp messages timing out

**Symptoms:** Long processing time causes WhatsApp timeout

**Solution:** Respond immediately with "Processing..." then send result:
```python
# Send immediate acknowledgment
await whatsapp_service.send_message(phone, "🎲 Processing your bet...")

# Process bet
bet, result = await game.play(...)

# Send final result
await whatsapp_service.send_message(phone, result_message)
```

---

## Next Steps

After completing Phase 3, proceed to:

### Phase 4: Admin Dashboard (Week 4-5)

- React frontend for admin panel
- User management interface
- Deposit/withdrawal approval UI
- Bet monitoring and analytics
- Match creation and settlement UI
- Financial reports and dashboards

### Phase 5: Testing & Beta (Week 5-6)

- Comprehensive system testing
- Closed beta with 50-300 users
- Performance monitoring
- Bug fixes and optimizations
- User feedback incorporation
- Final security audit

### Future Enhancements (Post-MVP)

- More game types (Dice, Crash, etc.)
- Live betting for Football
- Automated payment integration
- Push notifications
- Referral system
- Loyalty rewards program
- Mobile app (React Native)
- Advanced analytics dashboard
- AI-powered fraud detection

---

## Summary

Phase 3 delivers a complete gaming system with 4 distinct game types:

1. **Lucky Wheel**: Simple number guessing with 10x payout
2. **Color Game**: 4-color selection with 3x payout
3. **Pick 3**: High-risk jackpot game with 800x payout
4. **Football Yes/No**: Real-world event betting with variable odds

All games feature:
- Cryptographically secure random number generation
- Atomic financial transactions (ACID compliance)
- Complete audit trails
- WhatsApp integration
- Real-time balance updates
- Comprehensive error handling
- Protection against common betting bugs

The system is now ready for:
- Admin dashboard integration (Phase 4)
- Beta testing with real users (Phase 5)
- Production deployment

**Total Phase 3 Duration:** 10 days
**Key Achievement:** Fully functional betting platform with 4 games

---

**End of Phase 3 Implementation Plan**

