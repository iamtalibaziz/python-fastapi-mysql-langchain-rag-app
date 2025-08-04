import asyncio
import platform
from fastapi import FastAPI, Request
from app.models import user_model, chat_model, chat_session_model, document_model
from app.configs.database import engine
from app.controllers import auth_controller, user_controller, chat_controller, company_controller
from app.initial_data import create_initial_users
from app.helpers.response_helper import internal_server_error_response
from app.utils.logger import logger
from app.helpers.exceptions import CustomException
from app.middleware.exception_handler_middleware import custom_exception_handler, validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError, HTTPException

user_model.Base.metadata.create_all(bind=engine)
chat_model.Base.metadata.create_all(bind=engine)
chat_session_model.Base.metadata.create_all(bind=engine)
document_model.Base.metadata.create_all(bind=engine)

# Fix for RuntimeError: There is no current event loop in thread 'AnyIO worker thread'.
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(
    title="FastAPI MySQL Langchain RAG App",
    description="This is a sample application that demonstrates how to use FastAPI with MySQL, Langchain, and RAG.",
    version="1.0.0",
)

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unexpected error occurred: {exc}")
    return internal_server_error_response()

@app.on_event("startup")
def on_startup():
    create_initial_users()

app.include_router(auth_controller.router, tags=["Auth"], prefix="/api/auth")
app.include_router(user_controller.router, tags=["Users"], prefix="/api/users")
app.include_router(chat_controller.router, tags=["Chat"], prefix="/api/chat")
app.include_router(company_controller.router, tags=["Companies"], prefix="/api/companies")
