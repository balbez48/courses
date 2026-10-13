import os
from fastapi import FastAPI, HTTPException
import psycopg2

app = FastAPI(title="Course Service")

# Берем настройки подключения из переменных окружения
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "courses_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    """Вспомогательная функция для подключения к PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

#  Проверка жива ли БД и сам сервис
@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")  # Простейшая проверка отклика базы
        cursor.close()
        conn.close()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, hours, max_capacity FROM courses;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Преобразуем ответ из БД в формат JSON
        courses = [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "hours": row[3],
                "max_capacity": row[4]
            }
            for row in rows
        ]
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))