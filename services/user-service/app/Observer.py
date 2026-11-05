from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Dict, List
from app.models import User  # User теперь собирается через BuilderUser


# --- 1. ШАБЛОН ДЛЯ ПОДПИСЧИКОВ (Интерфейс) ---

class UserTableObserver(ABC):
    """Интерфейс наблюдателя за таблицей пользователей."""

    @abstractmethod
    def on_user_changed(self, action: str, user: User, admin_id: int) -> None:
        """Срабатывает при добавлении (INSERT), изменении (UPDATE) или удалении (DELETE)."""
        pass


# --- 2. КОНКРЕТНЫЕ ПОДПИСЧИКИ (Решают задачи из ТЗ) ---

class AuditLogObserver(UserTableObserver):
    """Записывает добавление, изменение ролей и удаление пользователей в протокол audit_logs."""

    def __init__(self):
        self.logs: List[Dict] = []
        self._next_id = 1

    def on_user_changed(self, action: str, user: User, admin_id: int) -> None:
        log_record = {
            "id": self._next_id,
            "user_id": admin_id,
            "action": f"{action} (role={user.role})",
            "entity_name": "users",
            "entity_id": user.user_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        self._next_id += 1
        self.logs.append(log_record)


class EmailNotificationObserver(UserTableObserver):
    """Формирует письма при создании пользователя или изменении его роли."""

    def __init__(self):
        self.sent_emails: List[Dict[str, str]] = []

    def on_user_changed(self, action: str, user: User, admin_id: int) -> None:
        if action == "INSERT":
            self.sent_emails.append({
                "email": user.email,
                "subject": "Регистрация в системе курсов",
                "body": f"Здравствуйте, {user.name}! Вам назначена роль: {user.role}.",
            })
        elif action == "UPDATE_ROLE":
            self.sent_emails.append({
                "email": user.email,
                "subject": "Изменение роли в системе",
                "body": f"Здравствуйте, {user.name}! Ваша новая роль: {user.role}.",
            })

class NewUserBroadcastObserver(UserTableObserver):
    """При создании пользователя формирует уведомление для всех уже существующих пользователей."""

    def __init__(self, get_all_emails: Callable[[], List[str]]):
        self._get_all_emails = get_all_emails
        self.messages: List[Dict[str, str]] = []

    def on_user_changed(self, action: str, user: User, admin_id: int) -> None:
        if action != "INSERT":
            return
        for email in self._get_all_emails():
            if email != user.email:  # самому новому пользователю уже отправлено приветствие
                self.messages.append({
                    "email": email,
                    "subject": "Новый пользователь в системе",
                    "body": f"В системе зарегистрирован новый пользователь: {user.name} ({user.role}).",
                })
