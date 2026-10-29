

class CourseService:
    def __init__(self, course_facade, course_repo):
        self.course_facade = course_facade
        self.course_repo = course_repo

    def add_course(self, data) -> dict:
        return self.course_facade.create_full_course(data)

    def get_all_courses(self):
        """Просматривать список курсов"""
        return self.course_repo.get_courses()

    def edit_course(self, course_id: int, data: dict):
        """Изменять информацию о курсах"""
        return self.course_repo.edit_record(course_id, data)

    def remove_course(self, course_id: int):
        """Удалять курсы"""
        return self.course_facade.delete_course_safely(course_id)

    def get_popular_courses(self):
        """Пока фильтр происходит по max_capacity.

        Нужно будет изменить на количество людей
        записавшихся в данный момент на курс
        """
        return self.course_repo.courses_filled()