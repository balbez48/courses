CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name_course VARCHAR(255) NOT NULL,
    description TEXT,
    hours INTEGER NOT NULL,
    creator VARCHAR(128) NOT NULL,
    max_capacity INTEGER NOT NULL CHECK (max_capacity > 0 AND max_capacity < 51)
);

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
