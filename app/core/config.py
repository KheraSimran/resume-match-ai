from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    chroma_host: str = 'localhost'
    chroma_port: int = 8001

    class Config:
        env_file = '.env'

settings = Settings()