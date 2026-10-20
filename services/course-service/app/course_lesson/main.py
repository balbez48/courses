from course_lesson import CourseLesson
from lesson_builder import BuilderCourseLesson
from lesson_decorator import LoggingCourseService
from lesson_repository import Record

builder = BuilderCourseLesson()
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



# standart_lesson = CourseLesson(1,1,1,'Python', 'www.stepik', 'create file')
# print(standart_lesson)
# dcit1 = {
#     "title": "Java",
#     "resource" : 'www.Java',
#     "homework" : 'delete file'
# }
# rec = Record("")
# rec.edit_record(1, dcit1)

# b = BuilderCourseLesson()
# l1 = b.set_course_id(1).set_form_data("A", "res").build()
# print(l1)
# l2 = b.set_course_id(2).set_form_data("B", "res").build()

# print(l1)
# print(l2)
# print(l1.title)

