from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from db.Database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # При остановке сервиса закрываем пул соединений
    if Database._instance is not None:
        Database().close()


app = FastAPI(title="Course Service", lifespan=lifespan)


# Проверка жива ли БД и сам сервис
@app.get("/health")
def health_check():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT 1;")  # Простейшая проверка отклика базы
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )


# Получение списка всех курсов
@app.get("/courses")
def get_courses():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT id, name, description, hours, max_capacity FROM courses;")
            rows = cur.fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "hours": row[3],
                "max_capacity": row[4]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))