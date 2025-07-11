from pathlib import Path

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv.load_dotenv()

PROJECT_DIR = Path(__file__).parent

THEME_DIR = PROJECT_DIR.joinpath("theme")
LOG_DIR = PROJECT_DIR.joinpath("logs")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    # == SERVER == #
    SERVER_READER_PORT: int = 31313


settings = Settings()  # type: ignore
