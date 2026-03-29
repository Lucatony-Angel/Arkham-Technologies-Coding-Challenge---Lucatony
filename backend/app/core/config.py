from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    eia_api_key: str

    class config:
        env_file = ".env"

settings = Settings()