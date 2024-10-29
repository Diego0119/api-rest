from advanced_alchemy.config.sync import SyncSessionConfig
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin, sync_autocommit_before_send_handler
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySyncConfig
from sqlalchemy.orm import DeclarativeBase

from app import settings

sqlalchemy_config = SQLAlchemySyncConfig(
    connection_string=settings.database_url.unicode_string(),
    session_config=SyncSessionConfig(expire_on_commit=False),
    before_send_handler=sync_autocommit_before_send_handler,
)
sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)


class Base(DeclarativeBase):
    pass
