from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    REDIS_HOST: str

    @property
    def DB_URL(self):
        return f"http://{self.DB_HOST}:{self.DB_PORT}"
    

settings = Settings(
    _env_file=".env",
    _env_file_encoding="utf-8"
)
