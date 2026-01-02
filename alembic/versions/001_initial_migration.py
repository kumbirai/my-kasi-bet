"""Initial migration: Add transaction, deposit, withdrawal, admin models, and admin action log

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table (must be first as other tables depend on it)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_blocked', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_active', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)

    # Create wallets table (depends on users)
    op.create_table(
        'wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_wallets_id'), 'wallets', ['id'], unique=False)
    op.create_index(op.f('ix_wallets_user_id'), 'wallets', ['user_id'], unique=False)

    # Create admin_users table
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=200), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'ADMIN', 'SUPPORT', name='adminrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_index(op.f('ix_admin_users_email'), 'admin_users', ['email'], unique=True)

    # Create transactions table (depends on users)
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('balance_before', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('balance_after', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('reference_type', sa.String(length=20), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('metadata', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_type'), 'transactions', ['type'], unique=False)
    op.create_index(op.f('ix_transactions_created_at'), 'transactions', ['created_at'], unique=False)
    op.create_index('ix_user_created', 'transactions', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_user_type', 'transactions', ['user_id', 'type'], unique=False)

    # Create bets table (depends on users)
    op.create_table(
        'bets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bet_type', sa.Enum('LUCKY_WHEEL', 'COLOR_GAME', 'PICK_3', 'FOOTBALL_YESNO', name='bettype'), nullable=False),
        sa.Column('stake_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('bet_data', sa.String(length=500), nullable=False),
        sa.Column('game_result', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'WON', 'LOST', 'REFUNDED', 'CANCELLED', name='betstatus'), nullable=False),
        sa.Column('multiplier', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payout_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('settled_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bets_id'), 'bets', ['id'], unique=False)
    op.create_index(op.f('ix_bets_user_id'), 'bets', ['user_id'], unique=False)
    op.create_index(op.f('ix_bets_bet_type'), 'bets', ['bet_type'], unique=False)
    op.create_index(op.f('ix_bets_status'), 'bets', ['status'], unique=False)
    op.create_index(op.f('ix_bets_created_at'), 'bets', ['created_at'], unique=False)
    op.create_index('ix_bets_user_created', 'bets', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_bets_user_type', 'bets', ['user_id', 'bet_type'], unique=False)
    op.create_index('ix_bets_status_created', 'bets', ['status', 'created_at'], unique=False)

    # Create matches table (no dependencies)
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('home_team', sa.String(length=100), nullable=False),
        sa.Column('away_team', sa.String(length=100), nullable=False),
        sa.Column('event_description', sa.String(length=200), nullable=False),
        sa.Column('yes_odds', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('no_odds', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'SETTLED', 'CANCELLED', name='matchstatus'), nullable=False),
        sa.Column('result', sa.Enum('YES', 'NO', name='matchresult'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('match_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settled_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_id'), 'matches', ['id'], unique=False)
    op.create_index(op.f('ix_matches_status'), 'matches', ['status'], unique=False)

    # Create deposits table
    op.create_table(
        'deposits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_method', sa.Enum('VOUCHER_1', 'SNAPSCAN', 'CAPITEC', 'BANK_TRANSFER', 'OTHER', name='paymentmethod'), nullable=False),
        sa.Column('proof_type', sa.String(length=20), nullable=True),
        sa.Column('proof_value', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', name='depositstatus'), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.String(length=200), nullable=True),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deposits_id'), 'deposits', ['id'], unique=False)
    op.create_index(op.f('ix_deposits_user_id'), 'deposits', ['user_id'], unique=False)
    op.create_index(op.f('ix_deposits_status'), 'deposits', ['status'], unique=False)
    op.create_index(op.f('ix_deposits_created_at'), 'deposits', ['created_at'], unique=False)

    # Create withdrawals table
    op.create_table(
        'withdrawals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('withdrawal_method', sa.Enum('BANK_TRANSFER', 'CASH_PICKUP', 'EWALLET', name='withdrawalmethod'), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('account_holder', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', name='withdrawalstatus'), nullable=False),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.String(length=200), nullable=True),
        sa.Column('debit_transaction_id', sa.Integer(), nullable=True),
        sa.Column('refund_transaction_id', sa.Integer(), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['debit_transaction_id'], ['transactions.id']),
        sa.ForeignKeyConstraint(['refund_transaction_id'], ['transactions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_withdrawals_id'), 'withdrawals', ['id'], unique=False)
    op.create_index(op.f('ix_withdrawals_user_id'), 'withdrawals', ['user_id'], unique=False)
    op.create_index(op.f('ix_withdrawals_status'), 'withdrawals', ['status'], unique=False)
    op.create_index(op.f('ix_withdrawals_created_at'), 'withdrawals', ['created_at'], unique=False)

    # Create admin_action_logs table
    op.create_table(
        'admin_action_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_action_logs_id'), 'admin_action_logs', ['id'], unique=False)
    op.create_index(op.f('ix_admin_action_logs_admin_id'), 'admin_action_logs', ['admin_id'], unique=False)
    op.create_index(op.f('ix_admin_action_logs_action_type'), 'admin_action_logs', ['action_type'], unique=False)
    op.create_index(op.f('ix_admin_action_logs_entity_type'), 'admin_action_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_admin_action_logs_entity_id'), 'admin_action_logs', ['entity_id'], unique=False)
    op.create_index(op.f('ix_admin_action_logs_created_at'), 'admin_action_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop admin_action_logs table
    op.drop_index(op.f('ix_admin_action_logs_created_at'), table_name='admin_action_logs')
    op.drop_index(op.f('ix_admin_action_logs_entity_id'), table_name='admin_action_logs')
    op.drop_index(op.f('ix_admin_action_logs_entity_type'), table_name='admin_action_logs')
    op.drop_index(op.f('ix_admin_action_logs_action_type'), table_name='admin_action_logs')
    op.drop_index(op.f('ix_admin_action_logs_admin_id'), table_name='admin_action_logs')
    op.drop_index(op.f('ix_admin_action_logs_id'), table_name='admin_action_logs')
    op.drop_table('admin_action_logs')

    # Drop withdrawals table
    op.drop_index(op.f('ix_withdrawals_created_at'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_status'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_user_id'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_id'), table_name='withdrawals')
    op.drop_table('withdrawals')

    # Drop deposits table
    op.drop_index(op.f('ix_deposits_created_at'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_status'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_user_id'), table_name='deposits')
    op.drop_index(op.f('ix_deposits_id'), table_name='deposits')
    op.drop_table('deposits')

    # Drop matches table
    op.drop_index(op.f('ix_matches_status'), table_name='matches')
    op.drop_index(op.f('ix_matches_id'), table_name='matches')
    op.drop_table('matches')

    # Drop bets table
    op.drop_index('ix_bets_status_created', table_name='bets')
    op.drop_index('ix_bets_user_type', table_name='bets')
    op.drop_index('ix_bets_user_created', table_name='bets')
    op.drop_index(op.f('ix_bets_created_at'), table_name='bets')
    op.drop_index(op.f('ix_bets_status'), table_name='bets')
    op.drop_index(op.f('ix_bets_bet_type'), table_name='bets')
    op.drop_index(op.f('ix_bets_user_id'), table_name='bets')
    op.drop_index(op.f('ix_bets_id'), table_name='bets')
    op.drop_table('bets')

    # Drop transactions table
    op.drop_index('ix_user_type', table_name='transactions')
    op.drop_index('ix_user_created', table_name='transactions')
    op.drop_index(op.f('ix_transactions_created_at'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_type'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')

    # Drop admin_users table
    op.drop_index(op.f('ix_admin_users_email'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_id'), table_name='admin_users')
    op.drop_table('admin_users')

    # Drop wallets table
    op.drop_index(op.f('ix_wallets_user_id'), table_name='wallets')
    op.drop_index(op.f('ix_wallets_id'), table_name='wallets')
    op.drop_table('wallets')

    # Drop users table
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS matchresult')
    op.execute('DROP TYPE IF EXISTS matchstatus')
    op.execute('DROP TYPE IF EXISTS betstatus')
    op.execute('DROP TYPE IF EXISTS bettype')
    op.execute('DROP TYPE IF EXISTS withdrawalstatus')
    op.execute('DROP TYPE IF EXISTS withdrawalmethod')
    op.execute('DROP TYPE IF EXISTS depositstatus')
    op.execute('DROP TYPE IF EXISTS paymentmethod')
    op.execute('DROP TYPE IF EXISTS adminrole')
