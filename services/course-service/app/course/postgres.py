from .models import Course
from .repository import CourseRepository

from psycopg2 import Error

class Record(CourseRepository): 
    def __init__(self, connect):
        self._conn = connect

    def add_record(self, course: Course) -> Course:
        cur = self._conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO courses (name_course, description, hours, creator, max_capacity)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name_course, description, hours, creator, max_capacity
                """,
                (course.name_course, course.description,
                 course.hours, course.creator, course.max_capacity),
            )
            
            row = cur.fetchone()
            self._conn.commit()
            
            course.id = row[0]
            return course
        
        except Error as e:
            self._conn.rollback()
            raise

        finally:
            cur.close()
    
    def remove_record(self, id) -> bool:
        cur = self._conn.cursor()
        try: 
            cur.execute(
                """
                DELETE FROM courses WHERE id = %s
                """,
                (id,),
            )

            cur_rows = cur.rowcount
            self._conn.commit()
            return cur_rows > 0
        
        except Error as e:
            self._conn.rollback()
            print(f"Ошибка удаления курса id={id}: {e}")
            return False
        
        finally:
            cur.close()

    def edit_record(self, id: int, data: dict) -> Course:
        fields = {k: v for k, v in data.items() if k in {"name_course", "description", "hours", "max_capacity"}}
        if not fields:
            raise ValueError("Нет полей для изменения")

        cur = self._conn.cursor()
        try:
            sets = ", ".join(f"{k} = %s" for k in fields)
            cur.execute(f"UPDATE courses SET {sets} WHERE id = %s \
                        RETURNING id, name_course, description, hours, creator, max_capacity",
                        (*fields.values(), id))
            
            row = cur.fetchone()
            if row is None:
                self._conn.rollback()
                raise LookupError(f"(course) id={id} не найден")
            
            self._conn.commit()
            return Course(*row)
        
        except Error as e:
            self._conn.rollback()
            raise

        finally:
            cur.close()