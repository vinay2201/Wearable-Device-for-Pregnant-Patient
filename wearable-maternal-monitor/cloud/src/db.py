from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from .config import SETTINGS

engine = create_engine(SETTINGS.mysql_url, pool_pre_ping=True)

def migrate():
    from pathlib import Path
    sql = Path(__file__).parent.parent / "sql" / "init.sql"
    with engine.begin() as conn:
        conn.connection.set_charset_collation('utf8mb4')
        conn.exec_driver_sql((sql).read_text())
