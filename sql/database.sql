CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(255) UNIQUE NOT NULL,
    pin VARCHAR(255) NOT NULL,
    is_voted BOOLEAN DEFAULT FALSE
);

CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    picture_url VARCHAR(255) NOT NULL,
    votes INT DEFAULT 0
);

CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    candidate_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Example of inserting an admin user (use a secure method for setting the password)
INSERT INTO admins (username, password) VALUES ('admin', '$2y$10$e4N8U6p0pjbF.EQTTm1A.eG/CxuawZ8F6tyW5P78axuB/6rH4Ai2m');
