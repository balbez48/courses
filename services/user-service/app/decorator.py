import logging
import threading
from typing import List, Optional

from app.Observer import UserTableObserver
from app.models import User
from app.repository import UserStorage

log = logging.getLogger(__name__)


class ObservedUserRepository(UserStorage):
    """Decorator: оборачивает любое хранилище пользователей и после каждой
    успешной операции оповещает наблюдателей (журнал, письма, рассылка).
    Сам репозиторий о наблюдателях ничего не знает."""

    def __init__(self, inner: UserStorage, observers: List[UserTableObserver]):
        self._inner = inner
        self._observers = observers
        self._lock = threading.Lock()  # наблюдатели хранят счётчики, запросы идут в разных потоках

    def _notify(self, action: str, user: User, admin_id: Optional[int]) -> None:
        with self._lock:
            for observer in self._observers:
                try:
                    observer.on_user_changed(action, user, admin_id)
                except Exception:
                    # Сбой наблюдателя не должен ломать уже выполненную операцию с БД
                    log.exception("Observer %s failed on %s", type(observer).__name__, action)

    # --- изменяющие операции: делегируем и оповещаем ---

    def insert(self, user, admin_id=None):
        created = self._inner.insert(user, admin_id)
        self._notify("INSERT", created, admin_id)
        return created

    def update(self, user, admin_id=None):
        old = self._inner.get_by_id(user.user_id)
        updated = self._inner.update(user, admin_id)
        if updated is not None:
            changed_role = old is not None and old.role != updated.role
            self._notify("UPDATE_ROLE" if changed_role else "UPDATE", updated, admin_id)
        return updated

    def delete(self, user_id, admin_id=None):
        old = self._inner.get_by_id(user_id)
        deleted = self._inner.delete(user_id, admin_id)
        if deleted and old is not None:
            self._notify("DELETE", old, admin_id)
        return deleted

    # --- чтение: просто делегируем ---

    def get_all(self):
        return self._inner.get_all()

    def get_by_id(self, user_id):
        return self._inner.get_by_id(user_id)

    def get_by_email(self, email):
        return self._inner.get_by_email(email)
