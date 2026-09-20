from typing import List, Any, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "Show me users who registered this month"})

class QueryResponse(BaseModel):
    question: str
    sql: str
    explanation: str
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float
    tables_used: List[str] = []
    confidence: Optional[float] = 1.0

class ExplainRequest(BaseModel):
    sql: str = Field(..., json_schema_extra={"example": "SELECT * FROM users WHERE created_at >= '2026-09-01';"})

class ExplainResponse(BaseModel):
    sql: str
    explanation: str
    tables_used: List[str]
    is_safe: bool
    validation_message: str

class ColumnSchema(BaseModel):
    name: str
    type: str
    primary_key: bool
    foreign_key: Optional[str] = None

class TableSchema(BaseModel):
    table_name: str
    columns: List[ColumnSchema]

class SchemaResponse(BaseModel):
    database_type: str
    tables: List[TableSchema]
    formatted_ddl: str
