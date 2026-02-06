from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.task import router as task_router
from .core.database import create_db_and_tables
from .models import User, Task  # Import models to register with SQLModel metadata


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Todo API with Authentication",
        description="A secure todo application API with JWT-based authentication and user isolation",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://localhost:3000:*"],  # Allow frontend origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Add exposed headers for authorization
        expose_headers=["Access-Control-Allow-Origin", "Authorization"],
    )

    # Include API routers
    app.include_router(auth_router)
    app.include_router(task_router)

    # Create database tables on startup
    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)