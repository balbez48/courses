from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from states import Enrollment


# --- МОДЕЛИ ДАННЫХ (Записи таблиц). ---

@dataclass
class AuditLog:
    """Запись журнала аудита (таблица audit_logs)."""
    id: int
    user_id: int
    action: str          # INSERT, UPDATE, DELETE
    entity_name: str     # Название таблицы/сущности
    entity_id: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Certificate:
    """Сертификат об окончании курса (таблица certificates)."""
    id: int
    enrollment_id: int
    certificate_code: str
    issued_at: datetime = field(default_factory=datetime.now)


# --- ИНТЕРФЕЙС НАБЛЮДАТЕЛЯ ---

class TableObserver(ABC):
    """Наблюдатель за операциями добавления, изменения и удаления в таблице."""

    @abstractmethod
    def on_record_changed(
        self,
        table_name: str,
        action: str,
        record: Any,
        user_id: int,
    ) -> None:
        """Вызывается автоматически при INSERT, UPDATE или DELETE записи."""


# --- СУБЪЕКТ (Таблица с операциями CRUD) ---

class Table:
    """Таблица БД с поддержкой подписчиков на изменение записей."""

    def __init__(self, name: str):
        self.name = name
        self._records: Dict[int, Any] = {}
        self._observers: List[TableObserver] = []

    def subscribe(self, observer: TableObserver) -> None:
        """Подключить обработчик событий к таблице."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: TableObserver) -> None:
        """Отключить обработчик событий от таблицы."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, action: str, record: Any, user_id: int) -> None:
        for observer in self._observers:
            observer.on_record_changed(self.name, action, record, user_id)

    def insert(self, record: Any, user_id: int = 0) -> Any:
        """Добавление новой записи в таблицу."""
        if record.id in self._records:
            raise ValueError(f"Запись с id={record.id} уже существует в {self.name}")
        self._records[record.id] = record
        self._notify("INSERT", record, user_id)
        return record

    def update(self, record: Any, user_id: int = 0) -> Any:
        """Изменение существующей записи в таблице."""
        if record.id not in self._records:
            raise KeyError(f"Запись с id={record.id} не найдена в {self.name}")
        self._records[record.id] = record
        self._notify("UPDATE", record, user_id)
        return record

    def delete(self, record_id: int, user_id: int = 0) -> Any:
        """Удаление записи из таблицы."""
        if record_id not in self._records:
            raise KeyError(f"Запись с id={record_id} не найдена в {self.name}")
        removed = self._records.pop(record_id)
        self._notify("DELETE", removed, user_id)
        return removed

    def get(self, record_id: int) -> Optional[Any]:
        return self._records.get(record_id)

    def all(self) -> List[Any]:
        return list(self._records.values())


# --- КОНКРЕТНЫЕ НАБЛЮДАТЕЛИ (Решают задачи проекта) ---

class AuditLogObserver(TableObserver):
    """Автоматически протоколирует добавление, изменение и удаление записей в audit_logs."""

    def __init__(self, audit_table: Table):
        self.audit_table = audit_table
        self._next_id = 1

    def on_record_changed(self, table_name: str, action: str, record: Any, user_id: int) -> None:
        log_entry = AuditLog(
            id=self._next_id,
            user_id=user_id,
            action=action,
            entity_name=table_name,
            entity_id=record.id,
        )
        self._next_id += 1
        self.audit_table.insert(log_entry, user_id=user_id)


class CertificateObserver(TableObserver):
    """Автоматически выпускает сертификат при переходе Enrollment в статус COMPLETED."""

    def __init__(self, certificates_table: Table):
        self.certificates_table = certificates_table
        self._next_id = 1

    def on_record_changed(self, table_name: str, action: str, record: Any, user_id: int) -> None:
        if table_name != "enrollments" or action not in ("INSERT", "UPDATE"):
            return

        if isinstance(record, Enrollment) and record.status == "COMPLETED":
            # Проверяем, не был ли сертификат уже выдан для этой записи
            already_issued = any(
                cert.enrollment_id == record.id for cert in self.certificates_table.all()
            )
            if not already_issued:
                short_hash = uuid.uuid4().hex[:6].upper()
                cert = Certificate(
                    id=self._next_id,
                    enrollment_id=record.id,
                    certificate_code=f"CERT-2026-{short_hash}",
                )
                self._next_id += 1
                self.certificates_table.insert(cert, user_id=user_id)

    def verify_by_code(self, code: str) -> Optional[Certificate]:
        """Поиск сертификата по уникальному коду для публичной проверки."""
        for cert in self.certificates_table.all():
            if cert.certificate_code == code:
                return cert
        return None


class EmailOutboxObserver(TableObserver):
    """Формирует JSON-пакеты писем при записи на курс и при выдаче сертификата."""

    def __init__(self, emails_by_listener: Dict[int, str]):
        self.emails_by_listener = emails_by_listener
        self.outbox: List[Dict[str, str]] = []

    def on_record_changed(self, table_name: str, action: str, record: Any, user_id: int) -> None:
        if table_name == "enrollments" and isinstance(record, Enrollment):
            email = self.emails_by_listener.get(record.listener_id)
            if not email:
                return

            if action == "INSERT" and record.status == "ENROLLED":
                self.outbox.append({
                    "email": email,
                    "subject": "Подтверждение записи на курс",
                    "body": f"Вы записаны на курс ID={record.course_id}. Статус: {record.status}.",
                })
            elif action == "UPDATE" and record.status == "COMPLETED":
                self.outbox.append({
                    "email": email,
                    "subject": "Курс успешно завершен",
                    "body": f"Поздравляем! Вы прошли курс ID={record.course_id} на 100%.",
                })