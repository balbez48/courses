from .models import Enrollment


class Record: 
    def __init__(self, connect):
        self._conn = connect

    def count_by_course(self, course_id: int, statuses: tuple[str, ...]) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM enrollments "
                "WHERE course_id = %s AND status = ANY(%s)",
                (course_id, list(statuses)),
            )
            count = cur.fetchone()[0]
            self._conn.commit()
            return count