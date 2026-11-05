from fastapi import FastAPI, Depends, Header
from db.Database import Database

app = FastAPI()
db = Database()

# def get_service(x_user_id: int = Header(...)):
#     conn = db._pool.getconn()
#     try:
#         yield build_course_service(conn, x_user_id)
#     finally:
#         db._pool.putconn(conn)


# @app.get('/enrollments/active-count')
# def active_count(service: EnrollmentService = Depends(get_service)):
#     return service.get_active_count()