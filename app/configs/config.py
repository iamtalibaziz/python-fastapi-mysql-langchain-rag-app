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
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_API_ENV: str = os.getenv("PINECONE_API_ENV")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

settings = Settings()
