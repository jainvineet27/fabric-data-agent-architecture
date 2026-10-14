import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_ssms_engine():
    server = os.getenv("SQL_SERVER_NAME", "localhost")
    database = os.getenv("SQL_DATABASE_NAME", "master")
    use_win_auth = os.getenv("USE_WINDOWS_AUTH", "true").lower() == "true"
    user = os.getenv("SQL_USERNAME", "")
    password = os.getenv("SQL_PASSWORD", "")
    driver = "{ODBC Driver 17 for SQL Server}"

    if use_win_auth:
        conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes;"
    else:
        conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"

    params = urllib.parse.quote_plus(conn_str)
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}")