class CourseLesson:
    def __init__(self, 
                 lesson_id: int | None = None, 
                 course_id: int | None = None, 
                 order_num: int | None = None, 
                 title: str | None = None, 
                 resource: str | None = None, 
                 homework: str | None = None):
        self.lesson_id = lesson_id
        self.course_id = course_id
        self.order_num = order_num
        self.title = title
        self.resource = resource
        self.homework = homework

    def __repr__(self):
        return f"<CourseLesson id={self.lesson_id} course_id={self.course_id} title='{self.title}' order={self.order_num}>"


class BuilderCourseLesson:
    def __init__(self):
        self._lesson = CourseLesson()

    def set_course_id(self, course_id: int):
        self._lesson.course_id = course_id
        return self

    def set_form_data(self, title: str, resource: str, homework: str | None = None):
        self._lesson.title = title
        self._lesson.resource = resource
        self._lesson.homework = homework
        return self

    def set_order_num(self, order_num: int):
        self._lesson.order_num = order_num
        return self

    def reset(self):
        self._lesson = CourseLesson()

        return self._lesson

    def build(self) -> CourseLesson:
        if not self._lesson.course_id:
            raise ValueError("course_id is a required field.")
        if not self._lesson.title:
            raise ValueError("The lesson should have a title.")
        cur_record = self._lesson
        self.reset()

        return cur_record