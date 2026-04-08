from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    openai_api_key: str
    chroma_host: str = 'localhost'
    chroma_port: int = 8001
    
    langchain_tracing_v2 : bool = True
    langchain_project: str = 'resume-match-ai-tracing'
    
    langsmith_tracing_v2: bool = True
    langsmith_endpoint: str = 'https://api.smith.langchain.com'
    langsmith_project: str = 'resume-match-ai-tracing'
    langsmith_api_key: str = ''

    model_config = ConfigDict(env_file=".env")

settings = Settings()