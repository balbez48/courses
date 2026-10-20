#крутой паттерн в котором 4 невероятных состояния
from abc import ABC, abstractmethod


class InvalidTransition(Exception):
    """Операция недопустима в текущем статусе записи."""


class EnrollmentState(ABC):
    """Состояние записи на курс. Каждый статус - отдельный класс."""

    name: str

    @abstractmethod
    def submit_lesson(self, enrollment: "Enrollment", progress_percent: int) -> None:
        """Слушатель сдал урок; progress_percent - общий прогресс после сдачи."""

    @abstractmethod
    def cancel(self, enrollment: "Enrollment") -> None:
        """Отмена записи."""

    def _forbidden(self, action: str):
        raise InvalidTransition(f"Нельзя выполнить '{action}' в статусе {self.name}")


class EnrolledState(EnrollmentState):
    name = "ENROLLED"

    def submit_lesson(self, enrollment, progress_percent):
        # Первая сданная домашка: ENROLLED -> IN_PROGRESS
        enrollment._set_state(InProgressState())
        # Курс из одного урока может завершиться сразу
        enrollment.state.submit_lesson(enrollment, progress_percent)

    def cancel(self, enrollment):
        enrollment._set_state(CancelledState())


class InProgressState(EnrollmentState):
    name = "IN_PROGRESS"

    def submit_lesson(self, enrollment, progress_percent):
        # 100% программы: IN_PROGRESS -> COMPLETED
        if progress_percent >= 100:
            enrollment._set_state(CompletedState())

    def cancel(self, enrollment):
        enrollment._set_state(CancelledState())


class CompletedState(EnrollmentState):
    name = "COMPLETED"

    def submit_lesson(self, enrollment, progress_percent):
        self._forbidden("submit_lesson")

    def cancel(self, enrollment):
        self._forbidden("cancel")


class CancelledState(EnrollmentState):
    name = "CANCELLED"

    def submit_lesson(self, enrollment, progress_percent):
        self._forbidden("submit_lesson")

    def cancel(self, enrollment):
        self._forbidden("cancel")


# Соответствие значения из БД и класса состояния
STATES = {s.name: s for s in (EnrolledState, InProgressState, CompletedState, CancelledState)}


class Enrollment:
    """Контекст: запись на курс. Поведение делегирует текущему состоянию."""

    def __init__(self, id: int, listener_id: int, course_id: int, status: str = "ENROLLED"):
        self.id = id
        self.listener_id = listener_id
        self.course_id = course_id
        self.state: EnrollmentState = STATES[status]()

    @property
    def status(self) -> str:
        return self.state.name

    def _set_state(self, state: EnrollmentState) -> None:
        self.state = state

    def submit_lesson(self, progress_percent: int) -> None:
        self.state.submit_lesson(self, progress_percent)

    def cancel(self) -> None:
        self.state.cancel(self)
