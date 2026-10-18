import os
import threading
from contextlib import contextmanager

from psycopg2 import pool


class Database:
    """Singleton: единственный объект, управляющий подключениями к PostgreSQL."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Double-checked locking: безопасно при одновременных запросах из разных потоков
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._pool = pool.ThreadedConnectionPool(
                        minconn=1,
                        maxconn=10,
                        host=os.getenv("DB_HOST", "localhost"),
                        port=os.getenv("DB_PORT", "5432"),
                        database=os.getenv("DB_NAME", "user_db"),
                        user=os.getenv("DB_USER", "postgres"),
                        password=os.getenv("DB_PASSWORD", "postgres"),
                    )
                    # Экземпляр сохраняется только после успешного создания пула,
                    # поэтому при недоступной БД следующий вызов попробует снова
                    cls._instance = instance
        return cls._instance

    @contextmanager
    def cursor(self):
        """Выдаёт курсор из пула; commit/rollback и возврат соединения - автоматически."""
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def close(self):
        """Закрывает все соединения и сбрасывает Singleton."""
        with Database._lock:
            self._pool.closeall()
            Database._instance = None
