"""añadir last_login a accounts_users

Revision ID: 793404e9a68f
Revises: f2d9d455cc8e
Create Date: 2024-10-30 20:38:26.712738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '793404e9a68f'
down_revision: Union[str, None] = 'f2d9d455cc8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts_users', sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('accounts_users', 'last_login')