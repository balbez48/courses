from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from pydantic import BaseModel

from app.Observer import AuditLogObserver, EmailNotificationObserver, NewUserBroadcastObserver
from app.Database import Database
from app.decorator import ObservedUserRepository
from app.models import BuilderUser, User
from app.repository import DuplicateEmailError, UserRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # При остановке сервиса закрываем пул соединений
    if Database._instance is not None:
        Database().close()


app = FastAPI(title="User Service", lifespan=lifespan)

# --- Сборка: репозиторий (Singleton БД внутри) + декоратор + наблюдатели ---
audit_log = AuditLogObserver()
email_notifier = EmailNotificationObserver()
broadcast = NewUserBroadcastObserver(lambda: [u.email for u in repo.get_all()])  # repo вызывается позже
repo = ObservedUserRepository(UserRepository(), [audit_log, email_notifier, broadcast])


# --- Схемы запросов ---
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "STUDENT"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


def user_to_dict(u: User) -> dict:
    return {"id": u.user_id, "name": u.name, "email": u.email, "role": u.role}


# --- Права доступа ---
def require_admin(x_admin_id: int = Header()) -> int:
    """Управлять справочником может только ADMIN (раздел 4 ТЗ).
    Пока вместо JWT администратор передаётся заголовком X-Admin-Id."""
    admin = repo.get_by_id(x_admin_id)
    if admin is None or admin.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Требуется роль ADMIN")
    return admin.user_id


@app.get("/health")
def health_check():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT 1;")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# --- Чтение ---
@app.get("/listeners")
def get_listeners(email: Optional[str] = None):
    """Список слушателей; с параметром ?email= - поиск по email."""
    if email is not None:
        found = repo.get_by_email(email)
        return [user_to_dict(found)] if found else []
    return [user_to_dict(u) for u in repo.get_all()]


@app.get("/listeners/{user_id}")
def get_listener(user_id: int):
    user = repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user_to_dict(user)


# --- Изменение (только ADMIN) ---
@app.post("/listeners", status_code=201)
def create_listener(body: UserCreate, admin_id: int = Depends(require_admin)):
    try:
        user = BuilderUser().set_form_data(body.name, body.email, body.role).build()
        return user_to_dict(repo.insert(user, admin_id))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DuplicateEmailError:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")


@app.patch("/listeners/{user_id}")
def update_listener(user_id: int, body: UserUpdate, admin_id: int = Depends(require_admin)):
    current = repo.get_by_id(user_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        # Берём текущие данные и подставляем только переданные поля
        name = body.name if body.name is not None else current.name
        email = body.email if body.email is not None else current.email
        role = body.role if body.role is not None else current.role
        user = BuilderUser().set_user_id(user_id).set_form_data(name, email, role).build()
        updated = repo.update(user, admin_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DuplicateEmailError:
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    if updated is None:  # удалили между чтением и записью
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user_to_dict(updated)


@app.delete("/listeners/{user_id}", status_code=204)
def delete_listener(user_id: int, admin_id: int = Depends(require_admin)):
    if not repo.delete(user_id, admin_id):
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return Response(status_code=204)


# --- Журнал и уведомления (то, что накопили наблюдатели) ---
@app.get("/audit-logs")
def get_audit_logs(admin_id: int = Depends(require_admin)) -> List[dict]:
    return audit_log.logs


@app.get("/notifications")
def get_notifications(admin_id: int = Depends(require_admin)):
    return {"emails": email_notifier.sent_emails, "broadcast": broadcast.messages}
