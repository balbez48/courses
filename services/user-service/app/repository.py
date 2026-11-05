from abc import ABC, abstractmethod
from typing import List, Optional

from psycopg2 import errors

from app.models import User
from app.Database import Database


class DuplicateEmailError(Exception):
    """Пользователь с таким email уже есть."""


class UserStorage(ABC):
    """Общий интерфейс хранилища. Его реализуют и репозиторий, и декоратор."""

    @abstractmethod
    def insert(self, user: User, admin_id: Optional[int] = None) -> User: ...

    @abstractmethod
    def update(self, user: User, admin_id: Optional[int] = None) -> Optional[User]: ...

    @abstractmethod
    def delete(self, user_id: int, admin_id: Optional[int] = None) -> bool: ...

    @abstractmethod
    def get_all(self) -> List[User]: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...


def _to_user(row) -> User:
    # Строка из БД уже проверена при записи, поэтому собираем User напрямую, без Builder
    return User(row[0], row[1], row[2], row[3])


class UserRepository(UserStorage):
    """Работа с таблицей listeners: INSERT, UPDATE, DELETE и чтение.
    admin_id здесь не нужен (его использует декоратор для журнала)."""

    def insert(self, user, admin_id=None):
        try:
            with Database().cursor() as cur:
                cur.execute(
                    "INSERT INTO listeners (name, email, role) VALUES (%s, %s, %s) "
                    "RETURNING id, name, email, role;",
                    (user.name, user.email, user.role),
                )
                return _to_user(cur.fetchone())
        except errors.UniqueViolation:
            raise DuplicateEmailError(user.email)

    def update(self, user, admin_id=None):
        try:
            with Database().cursor() as cur:
                cur.execute(
                    "UPDATE listeners SET name = %s, email = %s, role = %s WHERE id = %s "
                    "RETURNING id, name, email, role;",
                    (user.name, user.email, user.role, user.user_id),
                )
                row = cur.fetchone()
                return _to_user(row) if row else None
        except errors.UniqueViolation:
            raise DuplicateEmailError(user.email)

    def delete(self, user_id, admin_id=None):
        with Database().cursor() as cur:
            cur.execute("DELETE FROM listeners WHERE id = %s;", (user_id,))
            return cur.rowcount > 0

    def get_all(self):
        with Database().cursor() as cur:
            cur.execute("SELECT id, name, email, role FROM listeners ORDER BY id;")
            return [_to_user(r) for r in cur.fetchall()]

    def get_by_id(self, user_id):
        with Database().cursor() as cur:
            cur.execute("SELECT id, name, email, role FROM listeners WHERE id = %s;", (user_id,))
            row = cur.fetchone()
            return _to_user(row) if row else None

    def get_by_email(self, email):
        with Database().cursor() as cur:
            cur.execute(
                "SELECT id, name, email, role FROM listeners WHERE email = %s;",
                (email.strip().lower(),),
            )
            row = cur.fetchone()
            return _to_user(row) if row else None