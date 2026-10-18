from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from db.Database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # При остановке сервиса закрываем пул соединений
    if Database._instance is not None:
        Database().close()


app = FastAPI(title="User Service", lifespan=lifespan)


@app.get("/health")
def health_check():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT 1;")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# Получение списка слушателей
@app.get("/listeners")
def get_listeners():
    try:
        with Database().cursor() as cur:
            cur.execute("SELECT id, name, email, role FROM listeners;")
            rows = cur.fetchall()

        return [
            {"id": r[0], "name": r[1], "email": r[2], "role": r[3]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
