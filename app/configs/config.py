import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    PORT: int = int(os.getenv("PORT"))
    DB_HOST: str = os.getenv("DB_HOST")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD")
    PINECONE_REGION: str = os.getenv("PINECONE_REGION")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME")

settings = Settings()
