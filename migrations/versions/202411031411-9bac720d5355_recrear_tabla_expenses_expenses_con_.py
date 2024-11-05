"""Recrear tabla expenses_expenses con nuevas columnas

Revision ID: 9bac720d5355
Revises: 793404e9a68f
Create Date: 2024-11-03 14:11:13.364726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bac720d5355'
down_revision: Union[str, None] = '793404e9a68f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table('expenses_expenses')
    
    op.create_table(
        "expenses_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("datetime", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PAID', 'CANCELED', name='expensestatus'), nullable=False, server_default='PENDING'),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["accounts_users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

def downgrade():
    op.drop_table('expenses_expenses')