from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.dto import QueryRequest, QueryResponse
from app.services.sql_generator import SQLGeneratorService
from app.services.sql_validator import SQLValidator
from app.utils.formatter import QueryExecutor

router = APIRouter(tags=["Query"])

@router.post("/query", response_model=QueryResponse)
def process_natural_language_query(req: QueryRequest, db: Session = Depends(get_db)):
    if not req.question or not req.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question field cannot be empty."
        )

    # Step 1: Generate SQL from natural language question
    try:
        generated = SQLGeneratorService.generate_sql(req.question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SQL from question: {str(e)}"
        )

    raw_sql = generated.get("sql", "")
    explanation = generated.get("explanation", "")
    tables_used = generated.get("tables_used", [])
    confidence = generated.get("confidence", 1.0)

    # Step 2: Validate SQL Security & Guardrails
    is_valid, sanitized_sql, err_msg, validated_tables = SQLValidator.validate_and_format(raw_sql)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": err_msg,
                "generated_sql": raw_sql,
                "suggestion": "I can only execute read-only SELECT queries on valid database tables."
            }
        )

    # Step 3: Execute safe query against database
    try:
        columns, rows, execution_time_ms = QueryExecutor.execute_read_only_query(db, sanitized_sql)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Database Execution Error: {str(e)}",
                "sql": sanitized_sql
            }
        )

    return QueryResponse(
        question=req.question,
        sql=sanitized_sql,
        explanation=explanation,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        execution_time_ms=execution_time_ms,
        tables_used=validated_tables or tables_used,
        confidence=confidence
    )
