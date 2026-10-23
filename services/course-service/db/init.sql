CREATE TABLE IF NOT EXISTS course_lesson (
    lesson_id  SERIAL PRIMARY KEY,
    course_id  INT           NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
    order_num  INT           NOT NULL CHECK (order_num BETWEEN 1 AND 40),
    title      VARCHAR(128)  NOT NULL,
    resource   VARCHAR(256)  NOT NULL,
    homework   VARCHAR(2000)
);

CREATE INDEX IF NOT EXISTS idx_course_lesson_course ON course_lesson (course_id, order_num);

CREATE TABLE IF NOT EXISTS course_lesson (
    lesson_id  SERIAL PRIMARY KEY,
    course_id  INTEGER      NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
    order_num  INTEGER      NOT NULL,
    title      VARCHAR(255) NOT NULL,
    resource   TEXT,
    homework   TEXT
);

CREATE INDEX IF NOT EXISTS idx_course_lesson_course ON course_lesson (course_id, order_num);