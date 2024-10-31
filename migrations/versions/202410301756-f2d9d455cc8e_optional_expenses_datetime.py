"""Optional expenses.datetime and expenses.description

Revision ID: f2d9d455cc8e
Revises: 2ca0c7119d91
Create Date: 2024-10-30 17:56:44.430258

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f2d9d455cc8e"
down_revision: Union[str, None] = "2ca0c7119d91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# aca tuve que debugear por horas, no me dejaba correr la migracion, debido a que supuestamente sqlite no soporta 
# un alter table
def upgrade() -> None:
    op.create_table(
        'temp_expenses_expenses',
        sa.Column('id', sa.Integer, primary_key=True),  
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('datetime', sa.DateTime(), nullable=True),
    )

    op.execute(
        'INSERT INTO temp_expenses_expenses (description, datetime) '
        'SELECT description, datetime FROM expenses_expenses'
    )

    op.drop_table('expenses_expenses')

    op.rename_table('temp_expenses_expenses', 'expenses_expenses')


def downgrade() -> None:
    op.create_table(
        'temp_expenses_expenses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('datetime', sa.DateTime(), nullable=False),
    )

    op.execute(
        'INSERT INTO temp_expenses_expenses (description, datetime) '
        'SELECT description, datetime FROM expenses_expenses'
    )

    op.drop_table('expenses_expenses')
    op.rename_table('temp_expenses_expenses', 'expenses_expenses')
