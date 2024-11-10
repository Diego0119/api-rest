from pydantic import AnyUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False
    database_url: AnyUrl = AnyUrl("sqlite:///./test.sqlite3")
    secret_key: SecretStr = SecretStr("secret")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
