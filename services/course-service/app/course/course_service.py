from .models import Course
from .course_facade import CourseManagementFacade

class CourseService:
    def __init__(self, course_facade: CourseManagementFacade, course_repo):
        self.course_facade = course_facade
        self.course_repo = course_repo

    def add_course(self, data) -> dict:
        return self.course_facade.create_full_course(data)

    def get_all_courses(self):
        """Просматривать список курсов (по пункту ТЗ)"""
        return self.course_repo.get_all_records()

    def edit_course(self, course_id: int, data: dict):
        """Изменять информацию о курсах (по пункту ТЗ)"""
        return self.course_repo.edit_record(course_id, data)

    def remove_course(self, course_id: int):
        """Удалять курсы (по пункту ТЗ)"""
        # Здесь сервис может проверить бизнес-правила перед удалением
        return self.course_repo.remove_record(course_id)

    def get_popular_courses(self):
        """Получение списка популярных/заполненных курсов (по пункту ТЗ)"""
        # Логика подсчета популярности, о которой мы говорили ранее
        pass