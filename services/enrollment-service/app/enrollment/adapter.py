from abc import ABC, abstractmethod
from .postgres import Record
from psycopg2 import Error


class EnrollmentClient(ABC):
    @abstractmethod
    def get_active_count(self, course_id: int) -> int: ...


class EnrollmentServiceError(Exception):
    """enrollment-service недоступен или вернул ошибку."""


class EnrollmentAdapter(EnrollmentClient):
    ACTIVE_STATUSES = ("ENROLLED", "IN_PROGRESS")

    def __init__(self, record: Record):
        self._record = record

    def get_active_count(self, course_id: int) -> int:
        try:
            return self._record.count_by_course(course_id, self.ACTIVE_STATUSES)
        except Error as e:
            raise EnrollmentServiceError(
                f"Не удалось получить активные записи курса {course_id}: {e}"
            ) from e
        
            