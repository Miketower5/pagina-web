from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://gestor:secret@localhost:5432/gestor_gastos"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "changeme"
    debug: bool = False
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Mercado Pago
    mp_webhook_secret: str = ""
    mp_access_token: str = ""

    # Belvo
    belvo_secret_id: str = ""
    belvo_secret_password: str = ""
    belvo_env: str = "sandbox"  # sandbox | production

    # Encryption
    pgp_sym_key: str = "changeme"


settings = Settings()
