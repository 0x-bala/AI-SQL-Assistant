import re
from typing import Tuple, List, Set
import sqlglot
from sqlglot import exp
from app.config import get_settings
from app.services.schema_service import SchemaService

settings = get_settings()

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "SHUTDOWN", "COPY", "VACUUM",
    "PRAGMA", "ATTACH", "DETACH", "INTO", "RENAME", "REPLACE"
}

FORBIDDEN_FUNCTIONS_PG = {
    "pg_sleep", "pg_read_file", "pg_ls_dir", "version", "current_user",
    "session_user", "system_user"
}

class SQLValidationError(Exception):
    pass

class SQLValidator:
    @classmethod
    def validate_and_format(cls, sql_query: str) -> Tuple[bool, str, str, List[str]]:
        """
        Validates the SQL query.
        Returns: (is_valid, sanitized_sql, error_message, tables_used)
        """
        if not sql_query or not sql_query.strip():
            return False, "", "SQL query cannot be empty.", []

        query = sql_query.strip()
        
        # Strip trailing semicolon if present
        if query.endswith(";"):
            query = query[:-1].strip()

        # 1. Multi-statement check (detect multiple semicolons)
        if ";" in query:
            return False, "", "Multiple SQL statements in a single request are strictly forbidden.", []

        # 2. Basic Regex Blacklist Check (fast pre-filter)
        clean_upper = re.sub(r"'.*?'", "", query.upper())  # remove literals for checking
        sorted_forbidden = sorted(FORBIDDEN_KEYWORDS, key=len, reverse=True)
        for kw in sorted_forbidden:
            pattern = r"\b" + kw + r"\b"
            if re.search(pattern, clean_upper):
                return False, "", f"Operation '{kw}' is strictly forbidden. Only read-only SELECT queries are allowed.", []

        # 3. Check for suspicious functions
        for fn in FORBIDDEN_FUNCTIONS_PG:
            pattern = r"\b" + fn + r"\b"
            if re.search(pattern, query.lower()):
                return False, "", f"Execution of dangerous function '{fn}()' is prohibited.", []

        # 4. AST Parsing via sqlglot
        try:
            parsed_expressions = sqlglot.parse(query)
            if not parsed_expressions or len(parsed_expressions) == 0:
                return False, "", "Failed to parse SQL query structure.", []

            if len(parsed_expressions) > 1:
                return False, "", "Multiple SQL statements detected.", []

            root_expr = parsed_expressions[0]
            if root_expr is None:
                return False, "", "Invalid SQL syntax.", []

            # Ensure root expression is a SELECT or CTE (WITH clause)
            if not isinstance(root_expr, (exp.Select, exp.Union, exp.Expression)):
                return False, "", "Query must be a SELECT statement.", []

            # Check statement type
            stmt_type = root_expr.key.upper()
            if stmt_type not in ["SELECT", "WITH", "UNION"]:
                return False, "", f"Invalid query type '{stmt_type}'. Only SELECT statements are permitted.", []

            # 5. Extract and Validate Tables
            allowed_tables = set(t.lower() for t in SchemaService.get_allowed_tables())
            tables_used: Set[str] = set()

            for table_expr in root_expr.find_all(exp.Table):
                tbl_name = table_expr.name.lower()
                if tbl_name:
                    tables_used.add(tbl_name)

            # Check if all used tables are in allowed list
            if allowed_tables:
                unauthorized = tables_used - allowed_tables
                if unauthorized:
                    return False, "", f"Access to table(s) {list(unauthorized)} is not permitted or table does not exist.", list(tables_used)

            # 6. Apply LIMIT Clause Enforcement if missing
            sanitized_sql = query
            has_limit = False
            for child in root_expr.find_all(exp.Limit):
                has_limit = True
                break

            if not has_limit:
                max_limit = settings.MAX_QUERY_LIMIT
                sanitized_sql = f"{query} LIMIT {max_limit}"

            return True, sanitized_sql, "Query is safe and valid.", list(tables_used)

        except sqlglot.errors.ParseError as pe:
            return False, "", f"SQL Syntax Error: {str(pe)}", []
        except Exception as e:
            return False, "", f"SQL Validation Error: {str(e)}", []
