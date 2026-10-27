from abc import ABC, abstractmethod


class RolePermissionError(Exception):
    """Операция недопустима для текущей роли пользователя."""


class UserRoleState(ABC):
    """Состояние (роль) пользователя. Каждая роль - отдельный класс."""

    name: str

    @abstractmethod
    def can_manage_users(self) -> bool:
        """Может ли создавать, изменять и удалять пользователей в таблице."""

    @abstractmethod
    def can_manage_courses(self) -> bool:
        """Может ли создавать и редактировать курсы."""

    @abstractmethod
    def can_enroll(self) -> bool:
        """Может ли записываться на курсы как слушатель."""

    def _forbidden(self, action: str) -> None:
        raise RolePermissionError(f"Роль '{self.name}' не позволяет выполнить: {action}")


class StudentState(UserRoleState):
    name = "STUDENT"

    def can_manage_users(self) -> bool:
        return False

    def can_manage_courses(self) -> bool:
        return False

    def can_enroll(self) -> bool:
        return True


class TeacherState(UserRoleState):
    name = "TEACHER"

    def can_manage_users(self) -> bool:
        return False

    def can_manage_courses(self) -> bool:
        return True

    def can_enroll(self) -> bool:
        return False


class AdminState(UserRoleState):
    name = "ADMIN"

    def can_manage_users(self) -> bool:
        return True

    def can_manage_courses(self) -> bool:
        return True

    def can_enroll(self) -> bool:
        return True


# Соответствие значения роли из БД и класса состояния
ROLES = {r.name: r for r in (StudentState, TeacherState, AdminState)}


class User:
    """Класс пользователя. Получает роль и права через паттерн State."""

    def __init__(self, id: int, name: str, email: str, role: str = "STUDENT"):
        if role not in ROLES:
            raise ValueError(f"Неизвестная роль: {role}")
        self.id = id
        self.name = name
        self.email = email
        self.state: UserRoleState = ROLES[role]()

    @property
    def role(self) -> str:
        """Текущая роль пользователя (STUDENT, TEACHER, ADMIN)."""
        return self.state.name

    def set_role(self, new_role: str) -> None:
        """Смена роли пользователя через паттерн State."""
        if new_role not in ROLES:
            raise ValueError(f"Неизвестная роль: {new_role}")
        self.state = ROLES[new_role]()

    def check_can_manage_users(self) -> None:
        """Проверка права управлять таблицей пользователей."""
        if not self.state.can_manage_users():
            self.state._forbidden("управление справочником пользователей")