CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Добавляем тестовый курс с id = 101
INSERT INTO courses (id, name) 
VALUES (101, 'Архитектура программного обеспечения') 
ON CONFLICT (id) DO NOTHING;

-- Создаем таблицу уроков
CREATE TABLE IF NOT EXISTS course_lesson (
    lesson_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
    order_num INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    resource TEXT,
    homework TEXT
);

-- Создаем индекс
CREATE INDEX IF NOT EXISTS idx_course_lesson_course ON course_lesson (course_id, order_num);
