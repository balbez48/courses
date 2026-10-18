from course_lesson import CourseLesson
from builders import CourseLessonBuilder

builder = CourseLessonBuilder()
lesson = (
    builder
    .set_course_id(101)
    .set_form_data(
        
        title='Python',
        resource='www.psu.ru',
        homework='Вывести в консоль "Hello world"'
    )
    .set_order_num(1)
    .build())

print(lesson)