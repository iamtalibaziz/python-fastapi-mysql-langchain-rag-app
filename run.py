from app.main import app
import uvicorn
from app.configs.config import settings
from app.utils.logger import logger

if __name__ == "__main__":
    logger.info(f"Starting server on 0.0.0.0:{settings.PORT}")
    reload = settings.ENVIRONMENT == "development"
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=reload)
