import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ------------------------------------------------------------------------------
# 1. Check if a direct DATABASE_URL is defined (e.g. for PostgreSQL)
# ------------------------------------------------------------------------------
custom_db_url = os.getenv("DATABASE_URL")

if custom_db_url:
    connection_url = custom_db_url
else:
    # --------------------------------------------------------------------------
    # 2. Build connection using URL.create (Structured, Clean, No urllib needed!)
    # --------------------------------------------------------------------------
    use_win_auth = os.getenv("USE_WINDOWS_AUTH", "true").lower() == "true"

    query_params = {
        "driver": os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server"),
        "TrustServerCertificate": "yes",
    }
    if use_win_auth:
        query_params["trusted_connection"] = "yes"
    else:
        # Azure Synapse rejects Windows login; this opens the Microsoft sign-in popup instead
        query_params["Authentication"] = "ActiveDirectoryInteractive"

    connection_url = URL.create(
        drivername="mssql+pyodbc",
        username=None if use_win_auth else os.getenv("SQL_USERNAME"),
        password=None,
        host=os.getenv("SQL_SERVER_NAME", "localhost"),
        port=int(os.getenv("SQL_PORT")) if os.getenv("SQL_PORT") else None,
        database=os.getenv("SQL_DATABASE_NAME", "master"),
        query=query_params,
    )

# Create engine directly at module level
engine = create_engine(connection_url)

def get_ssms_engine():
    """Returns the created SQLAlchemy engine."""
    return engine


if __name__=="__main__":
    print(get_ssms_engine())
    

