import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import get_settings
from app.routes import health, schema, query, explain

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="A beginner-friendly AI SQL Assistant built with FastAPI, PostgreSQL, SQLAlchemy, AST Validation, and LLM Integration.",
    version="1.0.0",
    debug=settings.DEBUG
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(schema.router)
app.include_router(query.router)
app.include_router(explain.router)

# Mount Static Files for Web UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_homepage():
    return FileResponse(os.path.join(static_dir, "index.html"))
