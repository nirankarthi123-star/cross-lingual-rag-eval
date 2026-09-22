from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.api.routes import router as api_router
from backend.config.logging import setup_logging
from backend.config.settings import get_settings

logger = setup_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown routines."""
    logger.info("Starting up %s (Environment: %s)", settings.APP_NAME, settings.APP_ENV)
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)


def create_app() -> FastAPI:
    """Factory function to construct and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    import os

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API endpoints
    app.include_router(api_router)

    # Resolve the frontend directory path
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

    if os.path.isdir(frontend_dir):
        # Explicit page routes — must be registered BEFORE the static mount
        # so extensionless URLs always serve the correct HTML file.
        @app.get("/", include_in_schema=False)
        async def serve_chatbot():
            return FileResponse(os.path.join(frontend_dir, "index.html"))

        @app.get("/documents", include_in_schema=False)
        async def serve_documents():
            return FileResponse(os.path.join(frontend_dir, "documents.html"))

        @app.get("/dashboard", include_in_schema=False)
        async def serve_dashboard():
            return FileResponse(os.path.join(frontend_dir, "dashboard.html"))

        # Mount static files for assets (JS, CSS, images, etc.)
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    else:
        logger.warning(f"Frontend directory not found at {frontend_dir}")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
