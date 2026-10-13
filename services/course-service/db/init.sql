CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    hours INT NOT NULL CHECK (hours > 0),
    max_capacity INT NOT NULL DEFAULT 20 CHECK (max_capacity >= 0)
);