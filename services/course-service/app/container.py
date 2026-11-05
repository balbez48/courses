from db.Database import Database
from app.course.postgres import Record as CourseRecord
from app.course.repository import LoggingCourseRepository, AuditRepository as CourseAuditRepository
from app.course_lesson.postgres import Record as LessonRecord
from app.course_lesson.repository import LoggingLessonRepository, AuditRepository as LessonAuditRepository
from app.course.course_facade import CourseManagementFacade, CourseCreateData
from app.course.course_service import CourseService

def build_course_service(conn, user_id: int) -> CourseService:
    audit = CourseAuditRepository(conn)
    c_repo = LoggingCourseRepository(CourseRecord(conn), audit)
    l_repo = LoggingLessonRepository(LessonRecord(conn), LessonAuditRepository(conn))
    facade = CourseManagementFacade(c_repo, l_repo, None)
    return CourseService(facade, c_repo)