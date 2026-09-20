from fastapi import APIRouter
from app.models.dto import ExplainRequest, ExplainResponse
from app.services.sql_validator import SQLValidator

router = APIRouter(tags=["Explain"])

@router.post("/explain", response_model=ExplainResponse)
def explain_sql_query(req: ExplainRequest):
    sql = req.sql.strip()
    is_valid, sanitized_sql, msg, tables_used = SQLValidator.validate_and_format(sql)

    if not is_valid:
        explanation = f"Security Warning: This query is rejected because {msg}"
    else:
        tbl_str = ", ".join(tables_used) if tables_used else "database"
        explanation = f"This read-only SELECT query queries table(s) [{tbl_str}]. It retrieves specified matching rows and columns safely."

    return ExplainResponse(
        sql=sanitized_sql if is_valid else sql,
        explanation=explanation,
        tables_used=tables_used,
        is_safe=is_valid,
        validation_message=msg
    )
