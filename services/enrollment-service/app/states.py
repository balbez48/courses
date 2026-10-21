from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional


class InvalidTransition(Exception):
    """Операция недопустима в текущем статусе записи."""


# --- СОСТОЯНИЯ ЗАПИСИ (Управляют операциями в таблице) ---

class EnrollmentState(ABC):
    """Состояние записи на курс. Определяет, что можно делать с записью в таблице."""

    name: str

    @abstractmethod
    def submit_lesson(
        self,
        table: "EnrollmentTable",
        enrollment: "Enrollment",
        lesson_id: int,
        total_lessons: int,
    ) -> None:
        """Фиксация пройденного урока и обновление записи в таблице."""

    @abstractmethod
    def cancel(self, table: "EnrollmentTable", enrollment: "Enrollment") -> None:
        """Отмена записи и освобождение места в таблице."""

    @abstractmethod
    def can_delete(self) -> bool:
        """Разрешено ли физическое удаление записи из таблицы."""

    def _forbidden(self, action: str) -> None:
        raise InvalidTransition(f"Нельзя выполнить '{action}' в статусе {self.name}")


class EnrolledState(EnrollmentState):
    name = "ENROLLED"

    def submit_lesson(self, table, enrollment, lesson_id, total_lessons):
        # При первой сдаче урока: ENROLLED -> IN_PROGRESS
        enrollment._set_state(InProgressState())
        table.update(enrollment)
        # Передаем выполнение в состояние IN_PROGRESS для расчета прогресса
        enrollment.state.submit_lesson(table, enrollment, lesson_id, total_lessons)

    def cancel(self, table, enrollment):
        enrollment._set_state(CancelledState())
        table.update(enrollment)

    def can_delete(self) -> bool:
        return True


class InProgressState(EnrollmentState):
    name = "IN_PROGRESS"

    def submit_lesson(self, table, enrollment, lesson_id, total_lessons):
        # Добавляем урок в список пройденных и пересчитываем процент
        enrollment.completed_lessons.add(lesson_id)
        progress_percent = int((len(enrollment.completed_lessons) / total_lessons) * 100)

        # При достижении 100% программы: IN_PROGRESS -> COMPLETED
        if progress_percent >= 100:
            enrollment.finish_date = date.today()
            enrollment._set_state(CompletedState())

        # Сохраняем изменения записи в таблице
        table.update(enrollment)

    def cancel(self, table, enrollment):
        enrollment._set_state(CancelledState())
        table.update(enrollment)

    def can_delete(self) -> bool:
        return False  # Активное обучение нельзя удалить физически, только отменить


class CompletedState(EnrollmentState):
    name = "COMPLETED"

    def submit_lesson(self, table, enrollment, lesson_id, total_lessons):
        self._forbidden("submit_lesson")

    def cancel(self, table, enrollment):
        # Отмена доступна только до перехода в итоговый статус COMPLETED
        self._forbidden("cancel")

    def can_delete(self) -> bool:
        return False  # Завершенную запись с выданным сертификатом удалять нельзя


class CancelledState(EnrollmentState):
    name = "CANCELLED"

    def submit_lesson(self, table, enrollment, lesson_id, total_lessons):
        self._forbidden("submit_lesson")

    def cancel(self, table, enrollment):
        self._forbidden("cancel")

    def can_delete(self) -> bool:
        return True  # Отмененную запись можно удалить из таблицы


STATES = {s.name: s for s in (EnrolledState, InProgressState, CompletedState, CancelledState)}


# --- ЗАПИСЬ И ТАБЛИЦА (Контекст, в который встроен паттерн) ---

class Enrollment:
    """Запись в таблице enrollments."""

    def __init__(
        self,
        id: int,
        listener_id: int,
        course_id: int,
        status: str = "ENROLLED",
        enrollment_date: Optional[date] = None,
    ):
        self.id = id
        self.listener_id = listener_id
        self.course_id = course_id
        self.enrollment_date = enrollment_date or date.today()
        self.finish_date: Optional[date] = None
        self.completed_lessons: set[int] = set()
        self.state: EnrollmentState = STATES[status]()

    @property
    def status(self) -> str:
        return self.state.name

    def _set_state(self, state: EnrollmentState) -> None:
        self.state = state


class EnrollmentTable:
    """Система управления таблицей записей (добавление, изменение, удаление)."""

    def __init__(self):
        self._records: Dict[int, Enrollment] = {}
        self._next_id: int = 1

    def active_count_for_course(self, course_id: int) -> int:
        """Подсчет занятых мест (CANCELLED не учитываются в max_capacity)."""
        return sum(
            1 for r in self._records.values()
            if r.course_id == course_id and r.status != "CANCELLED"
        )

    def add_enrollment(self, listener_id: int, course_id: int, max_capacity: int) -> Enrollment:
        """Добавление записи на курс с проверкой свободных мест."""
        if self.active_count_for_course(course_id) >= max_capacity:
            raise ValueError("Нет свободных мест на курсе (превышен max_capacity)")

        record = Enrollment(id=self._next_id, listener_id=listener_id, course_id=course_id)
        self._records[record.id] = record
        self._next_id += 1
        return record

    def update(self, record: Enrollment) -> Enrollment:
        """Изменение записи в таблице."""
        if record.id not in self._records:
            raise KeyError(f"Запись id={record.id} не найдена в таблице")
        self._records[record.id] = record
        return record

    def delete(self, record_id: int) -> Enrollment:
        """Удаление записи из таблицы (разрешается или блокируется текущим состоянием)."""
        if record_id not in self._records:
            raise KeyError(f"Запись id={record_id} не найдена в таблице")

        record = self._records[record_id]
        if not record.state.can_delete():
            raise InvalidTransition(
                f"Удаление запрещено: запись id={record_id} находится в статусе {record.status}"
            )
        return self._records.pop(record_id)

    def submit_lesson(self, record_id: int, lesson_id: int, total_lessons: int) -> Enrollment:
        """Сдача урока слушателем через таблицу."""
        record = self._records[record_id]
        record.state.submit_lesson(self, record, lesson_id, total_lessons)
        return record

    def cancel_enrollment(self, record_id: int) -> Enrollment:
        """Отмена записи через таблицу (автоматически освобождает место на курсе)."""
        record = self._records[record_id]
        record.state.cancel(self, record)
        return record