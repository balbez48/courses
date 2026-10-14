from course_lesson import CourseLesson

class CourseLessonBuilder:
    def __init__(self):
        self._lesson = CourseLesson()

    def set_course_id(self, course_id: int):
        self._lesson.course_id = course_id
        return self  # Возвращаем self для цепочки вызовов (Fluent Interface)

    def set_form_data(self, title: str, resource: str, homework: str | None = None):
        self._lesson.title = title
        self._lesson.resource = resource
        self._lesson.homework = homework
        return self

    def set_order_num(self, order_num: int):
        self._lesson.order_num = order_num
        return self

    def build(self) -> CourseLesson:
        if not self._lesson.course_id:
            raise ValueError("course_id is a required field.")
        if not self._lesson.title:
            raise ValueError("The lesson should have a title.")
        
        return self._lesson