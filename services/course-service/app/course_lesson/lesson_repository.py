from course_lesson import CourseLesson
from psycopg2 import Error

class Record: 
    def __init__(self, connect):
        self._conn = connect

    def add_record(self, lesson: CourseLesson) -> CourseLesson:
        cur = self._conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO course_lesson (course_id, order_num, title, resource, homework)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING lesson_id
                """,
                (lesson.course_id, lesson.order_num, lesson.title,
                lesson.resource, lesson.homework),
            )
            lesson.lesson_id = cur.fetchone()[0]    # id выдала БД
            self._conn.commit()
            return lesson
        
        except Error as e:
            self._conn.rollback()
            raise

        finally:
            cur.close()
    
    def remove_record(self, lesson_id) -> bool:
        cur = self._conn.cursor()
        try: 
            cur.execute(
                """
                DELETE FROM course_lesson WHERE lesson_id = %s
                """,
                (lesson_id,),
            )

            cur_rows = cur.rowcount
            self._conn.commit()
            return cur_rows > 0
        
        except Error as e:
            self._conn.rollback()
            print(f"Ошибка удаления lesson_id={lesson_id}: {e}")
            return False
        
        finally:
            cur.close()

    def edit_record(self, lesson_id: int, data: dict) -> CourseLesson:
        fields = {k: v for k, v in data.items() if k in {"order_num", "title", "resource", "homework"}}
        if not fields:
            raise ValueError("Нет полей для изменения")

        cur = self._conn.cursor()
        try:
            sets = ", ".join(f"{k} = %s" for k in fields)
            cur.execute(f"UPDATE course_lesson SET {sets} WHERE lesson_id = %s \
                        RETURNING lesson_id, course_id, order_num, title, resource, homework",
                        (*fields.values(), lesson_id))
            
            row = cur.fetchone()
            if row is None:
                self._conn.rollback()
                raise LookupError(f"lesson_id={lesson_id} не найден")
            
            self._conn.commit()
            return CourseLesson(*row)
        
        except Error as e:
            self._conn.rollback()
            raise

        finally:
            cur.close()