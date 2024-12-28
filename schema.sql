CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    forename VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL
);

-- 4.2 Employee Table
CREATE TABLE employee (
    user_id INT PRIMARY KEY,
    salary DECIMAL(10,2) NOT NULL,
    emp_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 4.2 PoolAdmin Table
CREATE TABLE pool_admin (
    user_id INT PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES employee(user_id) ON DELETE CASCADE
);

-- 4.3 Lifeguard Table
CREATE TABLE lifeguard (
    user_id INT PRIMARY KEY,
    license_no VARCHAR(50) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES employee(user_id) ON DELETE CASCADE
);

-- 4.4 Coach Table
CREATE TABLE coach (
    user_id INT PRIMARY KEY,
    rank VARCHAR(50) NOT NULL,
    specialization VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES employee(user_id) ON DELETE CASCADE
);

-- 4.5 Swimmer Table
CREATE TABLE swimmer (
    user_id INT PRIMARY KEY,
    swimming_level VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- 4.6 Member Table
CREATE TABLE member (
    user_id INT PRIMARY KEY,
    free_training_remaining INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES swimmer(user_id) ON DELETE CASCADE
);