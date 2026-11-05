from fastapi import FastAPI, HTTPException, Depends, Header
from db.Database import Database
from .course.course_service import CourseService 
from .course.course_facade import LessonData, CourseCreateData
from app.course.enrollment_client import EnrollmentServiceError
from app.container import build_course_service

# delete происходит через фасад, фасад должен узнать у другого сервиса есть ли записи, поэтому пока не работает
# put где-то на этапе запроса к бд косяк
app = FastAPI()
db = Database()

def get_service(x_user_id: int = Header(...)):
    conn = db._pool.getconn()
    try:
        yield build_course_service(conn, x_user_id)
    finally:
        db._pool.putconn(conn)

# Эндпоинты для фронта
@app.post('/courses')
def create_course(data: CourseCreateData, service: CourseService = Depends(get_service)):
    return service.add_course(data)

@app.get('/courses')
def info_course(service: CourseService = Depends(get_service)):
    return service.get_all_courses()

@app.put('/courses/{id}')
def edit_course(id: int, data: CourseCreateData, service: CourseService = Depends(get_service)):
    return service.edit_course(id, data)

@app.delete('/courses/{id}')
def remove_course(id: int, service: CourseService = Depends(get_service)):
    try:
        return service.remove_course(id)
    except EnrollmentServiceError:
        raise HTTPException(status_code=503, detail="Сервис записей недоступен")


# Эндпоинты для Enrollment/фронт
@app.get('/courses/{course_id}')
def course_details(course_id: int, service: CourseService = Depends(get_service)):
    try:
        return service.get_course_details(course_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Курс не найден")