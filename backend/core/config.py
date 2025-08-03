from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    api_v1_str: str = "/api/v1"
    project_name: str = "Healthcare Communication Assistant"
    
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4-turbo-preview"
    
    data_dir: str = "./data"
    scenarios_dir: str = "./data/scenarios"
    results_dir: str = "./data/results"
    database_url: str = "sqlite:///./healthcare_app.db"
    
    backend_cors_origins: list = ["http://localhost:8501"]
    
    class Config:
        env_file = ".env"

settings = Settings()