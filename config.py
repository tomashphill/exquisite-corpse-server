from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Exquisite Corpse Server"

    class Config:
        env_file = ".env"