from typing import Dict, List, Optional
from states import User
from Observer import UserTableObserver, AuditLogObserver, EmailNotificationObserver


class UserTableSystem:
    """Система управления таблицей пользователей (добавление, изменение, удаление)."""

    def __init__(self):
        self._table: Dict[int, User] = {}
        self._next_id: int = 1
        self._observers: List[UserTableObserver] = []

    # --- Методы паттерна Observer ---

    def attach(self, observer: UserTableObserver) -> None:
        """Подключить наблюдателя к таблице пользователей."""
        self._observers.append(observer)

    def _notify(self, action: str, user: User, admin_id: int) -> None:
        """Оповестить все подписанные сервисы об изменении в таблице."""
        for observer in self._observers:
            observer.on_user_changed(action, user, admin_id)

    # --- Операции с таблицей пользователей (CRUD) ---

    def create_user(
        self,
        name: str,
        email: str,
        role: str = "STUDENT",
        admin: Optional[User] = None,
    ) -> User:
        """Добавление пользователя в таблицу и выдача ему роли через паттерн State."""
        # Если роль выше STUDENT, проверяем через паттерн State, что действие выполняет ADMIN
        if admin is not None:
            admin.check_can_manage_users()

        if self.find_by_email(email) is not None:
            raise ValueError(f"Пользователь с email {email} уже существует в таблице")

        user = User(id=self._next_id, name=name, email=email, role=role)
        self._table[user.id] = user
        self._next_id += 1

        admin_id = admin.id if admin else user.id
        self._notify("INSERT", user, admin_id)
        return user

    def update_role(self, user_id: int, new_role: str, admin: User) -> User:
        """Изменение роли пользователя в таблице (разрешено только ADMIN)."""
        admin.check_can_manage_users()

        if user_id not in self._table:
            raise KeyError(f"Пользователь с id={user_id} не найден")

        user = self._table[user_id]
        user.set_role(new_role)  # Смена роли через паттерн State
        self._notify("UPDATE_ROLE", user, admin.id)
        return user

    def update_user_info(self, user_id: int, name: str, email: str, admin: User) -> User:
        """Изменение сведений о пользователе в таблице."""
        admin.check_can_manage_users()

        if user_id not in self._table:
            raise KeyError(f"Пользователь с id={user_id} не найден")

        user = self._table[user_id]
        user.name = name
        user.email = email
        self._notify("UPDATE_INFO", user, admin.id)
        return user

    def delete_user(self, user_id: int, admin: User) -> User:
        """Удаление пользователя из таблицы."""
        admin.check_can_manage_users()

        if user_id not in self._table:
            raise KeyError(f"Пользователь с id={user_id} не найден")

        removed_user = self._table.pop(user_id)
        self._notify("DELETE", removed_user, admin.id)
        return removed_user

    def find_by_email(self, email: str) -> Optional[User]:
        """Поиск пользователя в таблице по email."""
        for user in self._table.values():
            if user.email == email:
                return user
        return None

    def get_all_users(self) -> List[User]:
        """Просмотр списка всех пользователей."""
        return list(self._table.values())