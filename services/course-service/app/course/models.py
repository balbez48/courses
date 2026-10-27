class Course:
    def __init__(self, 
                 id: int | None = None, 
                 name_course: str | None = None, 
                 description: str | None = None, 
                 hours: int | None = None, 
                 creator: str | None = None, 
                 max_capacity: int | None = None):
        self.id = id
        self.name_course = name_course
        self.description = description
        self.hours = hours
        self.creator = creator
        self.max_capacity = max_capacity

    def __repr__(self):
        return f"<Course id={self.id} name_course={self.name_course} description='{self.description}' creator={self.creator}>"


class BuilderCourse:
    def __init__(self):
        self._course = Course()

    def set_course_id(self, id: int):
        self._course.id = id
        return self

    def set_form_data(self, name_course: str, description: str, hours: int, max_capacity: int):
        self._course.name_course = name_course
        self._course.description = description
        self._course.hours = hours
        self._course.max_capacity = max_capacity
        return self

    def set_creator(self, creator: str):
        self._course.creator = creator
        return self

    def reset(self):
        self._course = Course()

        return self._course

    def build(self) -> Course:
        # if not self._course.id:
        #     raise ValueError("id is a required field.")
        if not self._course.creator:
            raise ValueError("The course should have a creator.")
        cur_record = self._course
        self.reset()

        return cur_record