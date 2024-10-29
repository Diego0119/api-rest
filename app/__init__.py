from litestar import Litestar

from app.config import settings
from app.database import sqlalchemy_plugin
from app.services.accounts.controllers import accounts_router
from app.services.accounts.security import oauth2_auth
from app.services.expenses.controllers import expenses_router

app = Litestar(
    route_handlers=[accounts_router, expenses_router],
    plugins=[sqlalchemy_plugin],
    on_app_init=[oauth2_auth.on_app_init],
    debug=settings.debug,
)
