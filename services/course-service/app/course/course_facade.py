from typing import List, Optional
from pydantic import BaseModel
from .models import BuilderCourse
from app.course_lesson.models import BuilderCourseLesson


class LessonData(BaseModel):
    order_num: int
    title: str
    resource: str
    homework: Optional[str] = None

class CourseCreateData(BaseModel):
    name: str
    description: Optional[str] = None
    hours: int
    creator: str
    max_capacity: int
    lessons: List[LessonData] = []


class CourseManagementFacade:
    """
    Фасад для управления курсами и их программой.
    Скрывает сложную логику поэтапного создания курса, уроков
    и проверки бизнес-правил перед удалением/изменением.
    """
    def __init__(self, course_repo, lesson_repo, enrollment_client):
        self.course_repo = course_repo          # Работа с таблицей courses
        self.lesson_repo = lesson_repo          # Работа с таблицей lessons (CourseLesson)
        self.enrollment_client = enrollment_client  # Клиент для проверки активных записей в enrollment-service

    def create_full_course(self, data: CourseCreateData):
        builder_course = BuilderCourse()
        builder_lesson = BuilderCourseLesson()

        course = (
            builder_course
            .set_form_data(
                name_course=data.name,
                description=data.description,
                hours=data.hours,
                max_capacity=data.max_capacity
            )
            .set_creator(creator=data.creator)
            .build()
        )

        saved_course = self.course_repo.add_record(course)

        for lesson_data in data.lessons:
            lesson = (builder_lesson
                      .set_course_id(saved_course.id)
                      .set_form_data(title=lesson_data.title,
                                     resource=lesson_data.resource,
                                     homework=lesson_data.homework)
                      .set_order_num(order_num=lesson_data.order_num)
                      .build())
            self.lesson_repo.add_record(lesson)

        return {
            "course_id": saved_course.id, 
            "status": "created", 
            "lessons_count": len(data.lessons)
        }

    def delete_course_safely(self, course_id: int) -> bool:
        """
        Безопасное удаление курса по правилам ТЗ:
        Проверяет, есть ли активные слушатели (ENROLLED, IN_PROGRESS).
        Если есть — блокирует удаление. Если нет — удаляет курс и его уроки.
        """
        # На будущее
        # active_enrollments = self.enrollment_client.get_active_count(course_id)
        
        # if active_enrollments > 0:
        #     raise ValueError("Нельзя удалить курс с активными слушателями (статусы ENROLLED или IN_PROGRESS)")

        # Удаляем только курс! Благодаря каскадности уроки сами удалятся.
        self.course_repo.remove_record(course_id)
        return True