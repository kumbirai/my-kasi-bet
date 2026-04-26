"""Add telegram_chat_id, nullable phone, identifier check

Revision ID: 002_telegram_mc
Revises: 001_initial
Create Date: 2026-04-11

"""
from alembic import op
import sqlalchemy as sa


revision = "002_telegram_mc"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("telegram_chat_id", sa.String(length=32), nullable=True),
    )
    op.create_index(
        op.f("ix_users_telegram_chat_id"),
        "users",
        ["telegram_chat_id"],
        unique=True,
    )
    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.create_check_constraint(
        "ck_users_phone_or_telegram",
        "users",
        sa.text("phone_number IS NOT NULL OR telegram_chat_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_phone_or_telegram", "users", type_="check")
    op.alter_column(
        "users",
        "phone_number",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.drop_index(op.f("ix_users_telegram_chat_id"), table_name="users")
    op.drop_column("users", "telegram_chat_id")
