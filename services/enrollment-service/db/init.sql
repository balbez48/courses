CREATE TYPE enrollment_status AS ENUM ('ENROLLED', 'IN_PROGRESS', 'COMPLETED');

CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    listener_id INT NOT NULL,  -- Внешний ID получаем из listener-service
    course_id INT NOT NULL,    -- Внешний ID получаем из course-service
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status enrollment_status NOT NULL DEFAULT 'ENROLLED'
);