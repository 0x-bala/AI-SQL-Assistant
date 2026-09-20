from typing import Dict, List, Any
from sqlalchemy import inspect
from app.database import engine
from app.models.dto import TableSchema, ColumnSchema, SchemaResponse

class SchemaService:
    @staticmethod
    def get_db_schema() -> SchemaResponse:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        tables_data: List[TableSchema] = []
        ddl_lines: List[str] = []

        db_type = engine.dialect.name.upper()

        for table in table_names:
            columns_info = inspector.get_columns(table)
            pk_constraint = inspector.get_pk_constraint(table)
            pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []
            fk_info = inspector.get_foreign_keys(table)

            fk_map = {}
            for fk in fk_info:
                for local_col, remote_col in zip(fk["constrained_columns"], fk["referred_columns"]):
                    fk_map[local_col] = f"{fk['referred_table']}.{remote_col}"

            col_schemas: List[ColumnSchema] = []
            table_ddl_cols: List[str] = []

            for col in columns_info:
                col_name = col["name"]
                col_type = str(col["type"])
                is_pk = col_name in pk_cols
                fk_target = fk_map.get(col_name)

                col_schemas.append(ColumnSchema(
                    name=col_name,
                    type=col_type,
                    primary_key=is_pk,
                    foreign_key=fk_target
                ))

                col_str = f"  {col_name} {col_type}"
                if is_pk:
                    col_str += " PRIMARY KEY"
                if fk_target:
                    col_str += f" REFERENCES {fk_target}"
                table_ddl_cols.append(col_str)

            tables_data.append(TableSchema(
                table_name=table,
                columns=col_schemas
            ))

            ddl_lines.append(f"CREATE TABLE {table} (\n" + ",\n".join(table_ddl_cols) + "\n);")

        formatted_ddl = "\n\n".join(ddl_lines)

        return SchemaResponse(
            database_type=db_type,
            tables=tables_data,
            formatted_ddl=formatted_ddl
        )

    @staticmethod
    def get_allowed_tables() -> List[str]:
        inspector = inspect(engine)
        return inspector.get_table_names()
