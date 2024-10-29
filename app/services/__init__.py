# ruff: noqa: F401
# This is neccessary to prevent errors when using SQLAlchemy mappings
from .accounts.models import User
from .expenses.models import Debt, Expense
