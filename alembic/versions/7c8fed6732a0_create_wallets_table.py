"""create wallets table

Revision ID: 7c8fed6732a0
Revises: 
Create Date: 2024-04-13 12:37:16.962577

"""
import uuid
from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7c8fed6732a0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wallets',
        sa.Column('id', sa.String(length=36), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('balance', sa.DECIMAL(precision=30, scale=18), default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=datetime.now, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=datetime.now, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('wallets')
