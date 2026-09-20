from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    db_engine = settings.DB_ENGINE
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "app_name": settings.APP_NAME,
        "database": {
            "engine": db_engine,
            "status": db_status
        },
        "llm_provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL
    }
