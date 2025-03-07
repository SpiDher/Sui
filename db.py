from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker


db_url = "sqlite+aiosqlite:///./database.db"


db_url = db_url.replace("postgresql://", "postgresql+asyncpg://") if db_url.startswith("postgresql://") else db_url
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