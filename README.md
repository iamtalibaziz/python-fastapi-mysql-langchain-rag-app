# FastAPI MySQL Langchain RAG App

This is a sample application that demonstrates how to use FastAPI with MySQL, Langchain, and RAG.

## Features

*   **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **MySQL**: A popular open-source relational database.
*   **SQLAlchemy**: A SQL toolkit and Object-Relational Mapper (ORM) for Python.
*   **Pydantic**: Data validation and settings management using Python type annotations.
*   **JWT Authentication**: Secure your endpoints with JSON Web Tokens.
*   **Role-Based Access Control (RBAC)**: Restrict access to certain endpoints based on user roles.
*   **Custom Exception Handling**: A robust system for handling and formatting exceptions.
*   **Async Support**: Asynchronous views for I/O-bound tasks.

## Getting Started

### Prerequisites

*   Python 3.7+
*   MySQL Server

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/python-fastapi-mysql-langchain-rag-app.git
    cd python-fastapi-mysql-langchain-rag-app
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**

    *   Create a MySQL database.
    *   Copy the `.env.example` file to `.env` and update the database connection details:

        ```env
        ENVIRONMENT=development
        PORT=8000
        DB_HOST=localhost
        DB_USER=your_db_user
        DB_PASSWORD=your_db_password
        DB_NAME=your_db_name
        JWT_SECRET=your_jwt_secret
        ```

5.  **Run the application:**

    ```bash
    python run.py
    ```

    The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

The API documentation is available at `http://127.0.0.1:8000/docs` (Swagger UI) and `http://127.0.0.1:8000/redoc` (ReDoc).

### Authentication (`/api/auth`)

*   `POST /signup`: Create a new user.
*   `POST /signin`: Authenticate a user and get a JWT token.
*   `POST /forgot-password`: Request a password reset token.
*   `POST /reset-password`: Reset the password using a reset token.

### Users (`/api/users`)

*   `GET /me/`: Get the details of the currently authenticated user.
*   `GET /`: Get a list of all users (admin only).
*   `GET /{user_id}`: Get the details of a specific user.
*   `PUT /{user_id}`: Update the details of a specific user.
*   `DELETE /{user_id}`: Delete a specific user.

## Project Structure

```
.
├── app
│   ├── configs
│   │   ├── config.py
│   │   └── database.py
│   ├── controllers
│   │   ├── auth_controller.py
│   │   └── user_controller.py
│   ├── helpers
│   │   ├── exceptions.py
│   │   └── response_helper.py
│   ├── middleware
│   │   ├── exception_handler_middleware.py
│   │   ├── role_checker.py
│   │   └── verify_access_token.py
│   ├── models
│   │   └── user_model.py
│   ├── schemas
│   │   └── user_schema.py
│   ├── services
│   │   ├── auth_service.py
│   │   └── user_service.py
│   ├── utils
│   │   └── logger.py
│   ├── initial_data.py
│   └── main.py
├── requirements.txt
├── run.py
└── .env.example
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
