"""create transactions table

Revision ID: d62916dc5177
Revises: 7c8fed6732a0
Create Date: 2024-04-13 12:56:59.175509

"""
import uuid
from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import VARCHAR

# revision identifiers, used by Alembic.
revision: str = 'd62916dc5177'
down_revision: Union[str, None] = '7c8fed6732a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(length=36), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('txid', sa.String(length=36), unique=True, default=uuid.uuid4, nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=30, scale=18), nullable=False),
        sa.Column('wallet_id', sa.String(length=36), sa.ForeignKey('wallets.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.now, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('transactions')
