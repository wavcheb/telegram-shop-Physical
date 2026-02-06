import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, QueuePool
from sqlalchemy.orm import declarative_base, sessionmaker

from bot.database.dsn import dsn
from bot.utils import SingletonMeta


class Database(metaclass=SingletonMeta):
    BASE = declarative_base()

    def __init__(self):
        connection_url = dsn()
        is_sqlite = connection_url.startswith("sqlite")

        engine_kwargs = dict(
            echo=False,  # Disable SQL logging (enable only for debug)
            pool_pre_ping=True,  # Check the connection before use
            future=True,  # Using SQLAlchemy 2.0 style
        )

        if not is_sqlite:
            # Production settings for MariaDB/MySQL
            engine_kwargs.update(
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=40,
                pool_timeout=30,
                pool_recycle=3600,
                connect_args={
                    "connect_timeout": 10,
                    "read_timeout": 30,
                    "write_timeout": 30,
                },
            )

        self.__engine: Engine = create_engine(connection_url, **engine_kwargs)

        # Pool state logging
        logging.info(f"Database pool initialized: size={20}, max_overflow={40}")

        self.__SessionLocal = sessionmaker(bind=self.__engine, autoflush=False, autocommit=False, future=True,
                                           expire_on_commit=False)

    @contextmanager
    def session(self):
        """Contextual session: guaranteed to close/rollback on error."""
        db = self.__SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @property
    def engine(self) -> Engine:
        return self.__engine
