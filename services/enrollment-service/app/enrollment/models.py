class Enrollment:
    def __init__(self, 
                 id: int,
                 listener_id: int,
                 course_id: int,
                 enrollment_date: str,
                 finish_date: str,
                 status: str):
        self.id = id
        self.listener_id = listener_id
        self.course_id = course_id
        self.enrollment_date = enrollment_date
        self.finish_date = finish_date
        self.status = status

    def __repr__(self):
        return f"<Enrollment id={self.id} listener_id={self.listener_id} course_id={self.course_id} enrollment_date='{self.enrollment_date}' finish_date={self.finish_date} status={self.status}>"
    

class BuilderEnrollment:
    def __init__(self):
        self._enroll = Enrollment()

    def set_enrollment_id(self, id: int):
        self._enroll.id = id
        return self

    def set_form_data(self, enrollment_date: str, finish_date: str | None, status: str):
        self._enroll.enrollment_date = enrollment_date
        self._enroll.finish_date = finish_date
        self._enroll.status = status
        return self

    def set_listener_id(self, listener_id: int):
        self._enroll.listener_id = listener_id
        return self

    def set_course_id(self, course_id: int):
            self._enroll.listener_id = course_id
            return self

    def reset(self):
        self._enroll = Enrollment()
        return self._enroll

    def build(self) -> Enrollment:
        if not self._enroll.listener_id:
            raise ValueError("listener_id is a required field.")
        if not self._enroll.course_id:
            raise ValueError("course_id is required field.")
        cur_record = self._enroll
        self.reset()

        return cur_record