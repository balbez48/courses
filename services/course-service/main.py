from db.Database import Database
from app.course.postgres import Record as CourseRecord
from app.course.repository import LoggingCourseRepository, AuditRepository as CourseAuditRepository
from app.course_lesson.postgres import Record as LessonRecord
from app.course_lesson.repository import LoggingLessonRepository, AuditRepository as LessonAuditRepository
from app.course.course_facade import CourseManagementFacade, CourseCreateData, LessonData

def main():
    # 1. Хардкод-данные (эмуляция пришедшего JSON-запроса от клиента)
    incoming_json_data = {
        "name": "Архитектура программного обеспечения",
        "description": "Курс по паттернам проектирования, репозиториям и фасадам в Python.",
        "hours": 36,
        "creator": "balbez48",
        "max_capacity": 30,
        "lessons": [
            {
                "order_num": 1,
                "title": "Введение в паттерны проектирования",
                "resource": "https://example.com/lesson1",
                "homework": "Изучить принципы SOLID"
            },
            {
                "order_num": 2,
                "title": "Репозитории и транзакции",
                "resource": "https://example.com/lesson2",
                "homework": "Реализовать метод edit_record"
            },
            {
                "order_num": 3,
                "title": "Паттерн Фасад",
                "resource": "https://example.com/lesson3",
                "homework": "Связать курсы и уроки через фасад"
            }
        ]
    }

    # 2. Валидируем входящие данные через Pydantic DTO
    try:
        course_create_dto = CourseCreateData(**incoming_json_data)
        print("Данные успешно прошли валидацию Pydantic!")
    except Exception as e:
        print(f"Ошибка валидации входящих данных: {e}")
        return

    # 3. Поднимаем соединение с БД и собираем репозитории
    db = Database()
    conn = db._pool.getconn()

    try:

        cur = conn.cursor()
        cur.execute("TRUNCATE courses CASCADE;")  # TRUNCATE очистит курсы и каскадно уроки, а также сбросит счетчик SERIAL ID
        conn.commit()
        cur.close()
        print("Таблицы успешно очищены для нового теста.")


        # Репозитории для курсов с поддержкой аудита/логирования
        course_db_repo = CourseRecord(conn)
        course_audit_repo = CourseAuditRepository(conn)
        logging_course_repo = LoggingCourseRepository(course_db_repo, course_audit_repo)

        # Репозитории для уроков с поддержкой аудита/логирования
        lesson_db_repo = LessonRecord(conn)
        lesson_audit_repo = LessonAuditRepository(conn)
        logging_lesson_repo = LoggingLessonRepository(lesson_db_repo, lesson_audit_repo)

        # Эмулятор внешнего микросервиса (enrollment-service) для проверки записей
        class MockEnrollmentClient:
            def get_active_count(self, course_id: int) -> int:
                return 0  # Студентов пока нет, удаление будет разрешено

        enrollment_client = MockEnrollmentClient()

        # 4. Создаем Фасад и передаем ему готовые зависимости через конструктор
        facade = CourseManagementFacade(
            course_repo=logging_course_repo,
            lesson_repo=logging_lesson_repo,
            enrollment_client=enrollment_client
        )

        # 5. Запускаем сценарий создания курса вместе со всеми уроками одним вызовом
        print("Создаем курс и 3 урока через Фасад...")
        result = facade.create_full_course(course_create_dto)
        
        print("\nСценарий успешно выполнен!")
        print(result)

    except Exception as e:
        print(f"\nПроизошла ошибка во время выполнения транзакции: {e}")
        conn.rollback()
    finally:
        # Всегда возвращаем соединение в пул
        db._pool.putconn(conn)
        print("Соединение с БД закрыто / возвращено в пул.")





    cur = conn.cursor()

    print("\n--- ТАБЛИЦА COURSES ---")
    cur.execute("SELECT * FROM courses;")
    for row in cur.fetchall():
        print(row)

    print("\n--- ТАБЛИЦА COURSE_LESSON ---")
    cur.execute("SELECT * FROM course_lesson;")
    for row in cur.fetchall():
        print(row)

    cur.close()

if __name__ == "__main__":
    main()


