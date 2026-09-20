from typing import Dict, Any
from app.services.schema_service import SchemaService
from app.services.llm_service import LLMService

class SQLGeneratorService:
    @staticmethod
    def generate_sql(question: str) -> Dict[str, Any]:
        # 1. Retrieve dynamic schema DDL
        schema_info = SchemaService.get_db_schema()
        ddl = schema_info.formatted_ddl

        # 2. Call LLM Service with prompt & schema
        llm_response = LLMService.generate_sql_from_question(
            question=question,
            schema_ddl=ddl
        )

        return llm_response
