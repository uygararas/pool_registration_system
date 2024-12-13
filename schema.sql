CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE pool (
    pool_id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(100),
    chlorine_level DECIMAL(5, 2)
);

CREATE TABLE session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT,
    pool_id INT,
    date DATE,
    start_time TIME,
    end_time TIME,
    FOREIGN KEY (pool_id) REFERENCES pool(pool_id)
);

CREATE TABLE booking (
    swimmer_id INT,
    session_id INT,
    PRIMARY KEY (swimmer_id, session_id),
    FOREIGN KEY (swimmer_id) REFERENCES user(user_id),
    FOREIGN KEY (session_id) REFERENCES session(session_id)
);