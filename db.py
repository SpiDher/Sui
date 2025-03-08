from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

debug_mode = os.getenv('DEBUG')  == 'True'

prod_db = os.getenv('DB_URL')

db_url =  prod_db


db_url = db_url.replace("postgresql://", "postgresql+asyncpg://") if prod_db and prod_db.startswith("postgresql://") else db_url

db_url = "sqlite+aiosqlite:///./database.db"
connect_args = {}  # No special args for PostgreSQL



engine = create_async_engine(url=db_url,connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(bind=engine)
Base = declarative_base()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()