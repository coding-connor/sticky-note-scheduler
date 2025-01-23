from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sticky Note Scheduler"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    # Base directory of the project
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # SQLite database file will be stored in the backend directory
    SQLITE_DB_FILE: str = "scheduler.db"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"sqlite:///{self.BASE_DIR / self.SQLITE_DB_FILE}"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
