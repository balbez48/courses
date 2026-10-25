from abc import ABC, abstractmethod
from .models import CourseLesson

class LessonRepository(ABC):
    @abstractmethod
    def add_record(self, lesson: CourseLesson) -> CourseLesson:
        """Метод для создания записи в CourseLesson(создание урока)"""
        
    
    @abstractmethod
    def remove_record(self, lesson_id: int) -> bool:
        """Метод для удаления записи из CourseLesson(удаление урока)"""
        

    @abstractmethod
    def edit_record(self, lesson_id: int, data: dict) -> CourseLesson:
        """
        Метод для изменения записи в CourseLesson

        Изменяет поля: "order_num", "title", "resource", "homework"
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
                INSERT INTO audit_logs (user_id, action_type,entity_name, entity_id)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, action_type,entity_name, entity_id)
            )
            self._conn.commit()
        finally:
            cur.close()   


class LoggingLessonRepository(LessonRepository):
    def __init__(self, wrapped: LessonRepository, log_report: AuditRepository):
        self._wrapped = wrapped
        self._log = log_report

    def add_record(self, lesson: CourseLesson) -> CourseLesson:
        created_lesson = self._wrapped.add_record(lesson)

        self._log.log_action(
            user_id=1,
            action_type='CREATE',
            entity_name='LESSON',
            entity_id=created_lesson.lesson_id
        )

        return created_lesson
        
    def remove_record(self, lesson_id: int) -> bool:
        is_deleted = self._wrapped.remove_record(lesson_id)

        if is_deleted:
            self._log.log_action(
                user_id=1,
                action_type='DELETE',
                entity_name='LESSON',
                entity_id=lesson_id
            )

        return is_deleted
    
    def edit_record(self, lesson_id: int, data: dict) -> CourseLesson:
        updated_lesson = self._wrapped.edit_record(lesson_id, data)

        self._log.log_action(
            user_id=1,
            action_type='EDIT',
            entity_name='LESSON',
            entity_id=lesson_id
        )

        return updated_lesson

