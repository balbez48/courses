from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from db.Database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # При остановке сервиса закрываем пул соединений
    if Database._instance is not None:
        Database().close()


app = FastAPI(title="Enrollment Service", lifespan=lifespan)


@app.get("/health")
def health_check():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT 1;")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# Получение списка записей на курсы
@app.get("/enrollments")
def get_enrollments():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT id, listener_id, course_id, enrollment_date, status FROM enrollments;")
            rows = cur.fetchall()

        return [
            {
                "id": r[0],
                "listener_id": r[1],
                "course_id": r[2],
                "enrollment_date": r[3],
                "status": r[4]
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))