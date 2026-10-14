import pandas as pd
from sqlalchemy import text
from fastmcp import FastMCP
from db_connection import get_ssms_engine

# Is Approach mein hum sirf SSMS tools banayenge kyunki Fabric Data Agent 
# pehle se hi Copilot UI (M365 Copilot / Copilot Studio / VS Code) mein published hai!
mcp = FastMCP("SSMS-Local-Plugin-For-Copilot-UI")
engine = get_ssms_engine()

@mcp.tool()
def list_ssms_tables() -> str:
    """List all tables in the local SSMS SQL Server database so the user can see them in Copilot UI."""
    query = """
    SELECT TABLE_SCHEMA, TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            return df.to_markdown(index=False) if not df.empty else "No tables found."
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def get_ssms_table_schema(table_name: str, schema_name: str = "dbo") -> str:
    """Inspect columns and data types of a local SSMS table from Copilot UI."""
    query = """
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
    ORDER BY ORDINAL_POSITION
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params={"schema": schema_name, "table": table_name})
            return df.to_markdown(index=False) if not df.empty else f"Table {schema_name}.{table_name} not found."
    except Exception as e:
        return f"Schema Error: {str(e)}"

@mcp.tool()
def execute_ssms_query(sql_query: str) -> str:
    """Run a SELECT query on local SSMS database and bring results into Copilot UI."""
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are permitted."
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql_query), conn)
            return df.to_markdown(index=False) if not df.empty else "0 rows returned."
    except Exception as e:
        return f"Query Error: {str(e)}"

if __name__ == "__main__":
    print("Running Approach 2 (SSMS-Only MCP Server for Copilot UI) on http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
