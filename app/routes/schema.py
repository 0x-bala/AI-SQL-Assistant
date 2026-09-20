from fastapi import APIRouter
from app.models.dto import SchemaResponse
from app.services.schema_service import SchemaService

router = APIRouter(tags=["Schema"])

@router.get("/schema", response_model=SchemaResponse)
def get_schema():
    return SchemaService.get_db_schema()
