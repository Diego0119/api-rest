from pydantic import AnyUrl, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False
    database_url: AnyUrl = AnyUrl("postgresql+psycopg:///shared_expenses")
    secret_key: Secret[str] = Secret("secret123")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
