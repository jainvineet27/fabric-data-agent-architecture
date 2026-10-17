import os
import sys

# Ensure current directory is in sys.path so sibling imports work everywhere
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import pandas as pd
from sqlalchemy import text
from fastmcp import FastMCP
from db_connection import get_ssms_engine
from fabric_client import query_fabric_via_fastmcp_client

mcp = FastMCP("Unified-SSMS-and-Fabric-Server")
engine = get_ssms_engine()

@mcp.tool()
def list_ssms_tables() -> str:
    """List all tables available in the local SQL Server (SSMS) database."""
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
    """Get column names and data types of a specific SQL Server table."""
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
    """Execute a read-only SELECT query on the local SQL Server (SSMS)."""
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are permitted."
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql_query), conn)
            return df.to_markdown(index=False) if not df.empty else "0 rows returned."
    except Exception as e:
        return f"Query Error: {str(e)}"

@mcp.tool()
async def ask_fabric_agent(question: str) -> str:
    """Ask a question to the published Microsoft Fabric Data Agent using fastmcp.Client."""
    try:
        return await query_fabric_via_fastmcp_client(question)
    except Exception as e:
        return f"Fabric Agent Error: {str(e)}"

if __name__ == "__main__":
    print("Running Approach 1 (Unified Gateway) on http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
