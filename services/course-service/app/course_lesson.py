class CourseLesson:
    def __init__(self, 
                 lesson_id: int | None = None, 
                 course_id: int | None = None, 
                 order_num: int | None = None, 
                 title: str | None = None, 
                 resource: str | None = None, 
                 homework: str | None = None):
        self.id = lesson_id
        self.course_id = course_id
        self.order_num = order_num
        self.title = title
        self.resource = resource
        self.homework = homework

    def __repr__(self):
        return f"<CourseLesson id={self.id} title='{self.title}' order={self.order_num}>"