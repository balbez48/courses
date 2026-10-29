from abc import ABC, abstractmethod
from .models import Course

class CourseRepository(ABC):
    @abstractmethod
    def get_courses(self) -> list[dict]:
        """Метод для получения списка курсов"""

    @abstractmethod
    def courses_filled(self) -> list[dict]:
        """Метод для получения списка популярных курсов
        (пока фильтрация происходить по max_capacity)
        """

    @abstractmethod
    def add_record(self, course: Course) -> Course:
        """Метод для создания записи в Course(создание курса)"""
    
    @abstractmethod
    def remove_record(self, id: int) -> bool:
        """Метод для удаления записи из Course(удаление курса)"""
        
    @abstractmethod
    def edit_record(self, id: int, data: dict) -> Course:
        """
        Метод для изменения записи в Course

        Изменяет поля: "name_course", "description", "hours", "max_capacity"
        Можно передать любое подмножество этих полей.
        """


class AuditRepository:
    def __init__(self, conn):
        self._conn = conn

    def log_action(self,
                   user_id: int, 
                   action_type: str,
                   entity_name: str, 
                   entity_id: int):
        cur = self._conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO audit_logs (user_id, action_type, entity_name, entity_id)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, action_type,entity_name, entity_id)
            )
            self._conn.commit()
        finally:
            cur.close()

    def get_logs(self, limit: int = 20) -> list[dict]:
        """Последние записи журнала (новые сверху)."""
        cur = self._conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, user_id, action_type, entity_name, entity_id, created_at
                FROM audit_logs
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (limit,)
            )
            columns = [d[0] for d in cur.description]
            rows = cur.fetchall()
            self._conn.commit()   # закрываем транзакцию
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cur.close()


class LoggingCourseRepository(CourseRepository):
    def __init__(self, wrapped: CourseRepository, log_report: AuditRepository):
        self._wrapped = wrapped
        self._log = log_report

    def get_courses(self) -> list[dict]:
        return self._wrapped.get_courses() 

    def courses_filled(self) -> list[dict]:
        return self._wrapped.courses_filled()    

    def add_record(self, course: Course) -> Course:
        created_course = self._wrapped.add_record(course)

        self._log.log_action(
            user_id=1,
            action_type='CREATE',
            entity_name='COURSE',
            entity_id=created_course.id
        )

        return created_course
        
    def remove_record(self, id: int) -> bool:
        is_deleted = self._wrapped.remove_record(id)

        if is_deleted:
            self._log.log_action(
                user_id=1,
                action_type='DELETE',
                entity_name='COURSE',
                entity_id=id
            )

        return is_deleted
    
    def edit_record(self, id: int, data: dict) -> Course:
        updated_course = self._wrapped.edit_record(id, data)

        self._log.log_action(
            user_id=1,
            action_type='EDIT',
            entity_name='COURSE',
            entity_id=id
        )

        return updated_course