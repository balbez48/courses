from db.Database import Database
from app.course_lesson.models import BuilderCourseLesson
from app.course_lesson.postgres import Record
from app.course_lesson.repository import LoggingLessonRepository, AuditRepository

builder = BuilderCourseLesson()




courseId = 101
while True :

    title = input('Название урока: ')
    resource = input('Ссылка на урок: ')
    homework = input('Домашнее задание: ')
    order_num = int(input('Номер урока: '))

    try:
        db = Database()
        conn = db._pool.getconn()
        system = Record(conn)
        audit_system = AuditRepository(conn)
        log_system = LoggingLessonRepository(system, audit_system)

        lesson = builder.set_course_id(courseId).set_form_data(title, resource, homework).set_order_num(order_num).build()
        log_system.add_record(lesson)
        print("Урок успешно добавлен и залогирован!")
    finally:
        db._pool.putconn(conn)

    answer = input('Закончить? (y/n): ')
    if answer.lower() == 'y':
        break


