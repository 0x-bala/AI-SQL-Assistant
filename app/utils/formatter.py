import time
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import get_settings

settings = get_settings()

class QueryExecutor:
    @staticmethod
    def execute_read_only_query(db: Session, sql_query: str) -> Tuple[List[str], List[List[Any]], float]:
        start_time = time.perf_counter()

        # Execute query within a read-only transaction boundary
        cursor = db.execute(text(sql_query))

        columns = list(cursor.keys())
        raw_rows = cursor.fetchall()

        formatted_rows = []
        for row in raw_rows:
            formatted_row = []
            for item in row:
                if hasattr(item, "isoformat"):
                    formatted_row.append(item.isoformat())
                else:
                    formatted_row.append(item)
            formatted_rows.append(formatted_row)

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return columns, formatted_rows, execution_time_ms
