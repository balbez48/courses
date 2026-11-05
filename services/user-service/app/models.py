import re

ROLES = ("STUDENT", "TEACHER", "ADMIN")  # справочник ролей из ТЗ
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User:
    def __init__(self,
                 user_id: int | None = None,
                 name: str | None = None,
                 email: str | None = None,
                 role: str | None = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role

    def __repr__(self):
        return f"<User id={self.user_id} email='{self.email}' role={self.role}>"


class BuilderUser:
    def __init__(self):
        self._user = User()

    def set_user_id(self, user_id: int):
        self._user.user_id = user_id
        return self

    def set_form_data(self, name: str, email: str, role: str = "STUDENT"):
        self._user.name = name
        self._user.email = email
        self._user.role = role
        return self

    def reset(self):
        self._user = User()

        return self._user

    def build(self) -> User:
        name = (self._user.name or "").strip()
        email = (self._user.email or "").strip().lower()  # email - это логин, регистр не важен

        if not name or len(name) > 100:
            raise ValueError("Имя обязательно, не длиннее 100 символов")
        if len(email) > 100 or not EMAIL_RE.match(email):
            raise ValueError("Некорректный email")
        if self._user.role not in ROLES:
            raise ValueError(f"Неизвестная роль: {self._user.role}. Допустимо: {', '.join(ROLES)}")

        self._user.name = name
        self._user.email = email
        cur_record = self._user
        self.reset()

        return cur_record
