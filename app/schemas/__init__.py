"""
Pydantic schemas package.

This package contains all Pydantic schemas for request/response validation.
"""
from app.schemas.admin import (
    AdminActionLogResponse,
    AdminUserCreate,
    AdminUserLogin,
    AdminUserResponse,
    PaginatedResponse,
    TokenResponse,
)
from app.schemas.deposit import (
    AdminDepositCreate,
    DepositApproval,
    DepositCreate,
    DepositRejection,
    DepositResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserWithWallet,
    WalletResponse,
)
from app.schemas.wallet import (
    TransactionBase,
    TransactionCreate,
    TransactionHistoryResponse,
    TransactionResponse,
    WalletBalanceResponse,
)
from app.schemas.withdrawal import (
    WithdrawalApproval,
    WithdrawalCreate,
    WithdrawalRejection,
    WithdrawalResponse,
)

__all__ = [
    "AdminActionLogResponse",
    "AdminDepositCreate",
    "AdminUserCreate",
    "AdminUserLogin",
    "AdminUserResponse",
    "DepositApproval",
    "DepositCreate",
    "DepositRejection",
    "DepositResponse",
    "PaginatedResponse",
    "TokenResponse",
    "TransactionBase",
    "TransactionCreate",
    "TransactionHistoryResponse",
    "TransactionResponse",
    "UserBase",
    "UserCreate",
    "UserResponse",
    "WalletBalanceResponse",
    "WalletResponse",
    "UserWithWallet",
    "WithdrawalApproval",
    "WithdrawalCreate",
    "WithdrawalRejection",
    "WithdrawalResponse",
]
