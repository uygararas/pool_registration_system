CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    forename VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL
);

-- 4.1 Employee Table
CREATE TABLE employee (
    user_id INT PRIMARY KEY,
    salary DECIMAL(10,2) DEFAULT 17002,
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


-- 4.7 PhoneNumber Table
CREATE TABLE IF NOT EXISTS phoneNumber (
    phone_number VARCHAR(20) PRIMARY KEY,
    swimmer_id INT NOT NULL,
    FOREIGN KEY (swimmer_id) REFERENCES swimmer(user_id) ON DELETE CASCADE
);

-- 4.12 Pool Table
CREATE TABLE IF NOT EXISTS pool (
    pool_id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    chlorine_level DECIMAL(5,2) NOT NULL
);

-- 4.11 Lane Table
CREATE TABLE IF NOT EXISTS lane (
    pool_id INT NOT NULL,
    lane_no INT NOT NULL,
    PRIMARY KEY (pool_id, lane_no),
    FOREIGN KEY (pool_id) REFERENCES pool(pool_id) ON DELETE CASCADE
);

-- 4.8 Session Table
CREATE TABLE IF NOT EXISTS session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT,
    pool_id INT NOT NULL,
    lane_no INT NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (pool_id, lane_no) REFERENCES lane(pool_id, lane_no) ON DELETE CASCADE
);

-- 4.9 Booking Table
CREATE TABLE IF NOT EXISTS booking (
    swimmer_id INT NOT NULL,
    session_id INT NOT NULL,
    PRIMARY KEY (swimmer_id, session_id),
    FOREIGN KEY (swimmer_id) REFERENCES swimmer(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE
);

-- 4.10 Guards Table
CREATE TABLE IF NOT EXISTS guards (
    lifeguard_id INT NOT NULL,
    session_id INT NOT NULL,
    PRIMARY KEY (lifeguard_id, session_id),
    FOREIGN KEY (lifeguard_id) REFERENCES lifeguard(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE
);

-- 4.13 FreeSession Table
CREATE TABLE IF NOT EXISTS freeSession (
    session_id INT PRIMARY KEY,
    FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE
);

-- 4.14 Lesson Table
CREATE TABLE IF NOT EXISTS lesson (
    session_id INT PRIMARY KEY,
    coach_id INT NOT NULL,
    student_count INT NOT NULL ,
    capacity INT NOT NULL check(capacity >= student_count),
    session_type ENUM('FemaleOnly', 'MaleOnly', 'Mixed') NOT NULL DEFAULT 'Mixed',
    FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (coach_id) REFERENCES coach(user_id) ON DELETE CASCADE
);


-- 4.15 OneToOneTraining Table
CREATE TABLE IF NOT EXISTS oneToOneTraining (
    session_id INT PRIMARY KEY,
    coach_id INT NOT NULL,
    swimming_style VARCHAR(100) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (coach_id) REFERENCES coach(user_id) ON DELETE CASCADE
);

-- 4.16 Report Table
CREATE TABLE IF NOT EXISTS report (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    report_name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    content TEXT,
    number_of_swimmer INT,
    number_of_lifeguard INT,
    most_liked_lesson VARCHAR(255),
    most_liked_coach VARCHAR(255),
    average_queue_length DECIMAL(5,2),
    FOREIGN KEY (admin_id) REFERENCES pool_admin(user_id) ON DELETE CASCADE
);

-- 4.17 Review Table
CREATE TABLE IF NOT EXISTS review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comment TEXT,
    rating DECIMAL(2,1) CHECK (rating >= 0 AND rating <= 5),
    FOREIGN KEY (user_id) REFERENCES swimmer(user_id) ON DELETE CASCADE
);

-- 4.18 CoachReview Table
CREATE TABLE IF NOT EXISTS coachReview (
    review_id INT PRIMARY KEY,
    coach_id INT NOT NULL,
    FOREIGN KEY (review_id) REFERENCES review(review_id) ON DELETE CASCADE,
    FOREIGN KEY (coach_id) REFERENCES coach(user_id) ON DELETE CASCADE
);

-- 4.19 LessonReview Table
CREATE TABLE IF NOT EXISTS lessonReview (
    review_id INT PRIMARY KEY,
    lesson_id INT NOT NULL,
    FOREIGN KEY (review_id) REFERENCES review(review_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(session_id) ON DELETE CASCADE
);

-- 4.20 WaitingQueue Table
CREATE TABLE IF NOT EXISTS waitQueue (
    lesson_id INT PRIMARY KEY,
    number_of_waiting INT NOT NULL DEFAULT 0,
    FOREIGN KEY (lesson_id) REFERENCES lesson(session_id) ON DELETE CASCADE
);

-- 4.21 SwimmerWaitQueue Table
CREATE TABLE IF NOT EXISTS swimmerWaitQueue (
    swimmer_id INT NOT NULL,
    lesson_id INT NOT NULL,
    request_date DATE NOT NULL,
    PRIMARY KEY (swimmer_id, lesson_id),
    FOREIGN KEY (swimmer_id) REFERENCES member(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES waitQueue(lesson_id) ON DELETE CASCADE
);

-- Views
CREATE VIEW SessionsWithoutLifeguard AS
SELECT 
    s.session_id, 
    p.location AS pool_location, 
    s.lane_no, 
    s.date, 
    s.start_time, 
    s.end_time
FROM session s
JOIN pool p ON s.pool_id = p.pool_id
LEFT JOIN guards g ON s.session_id = g.session_id
WHERE g.lifeguard_id IS NULL;


CREATE VIEW swimmer_booked_sessions AS
SELECT 
    b.swimmer_id,
    s.session_id, 
    s.description, 
    s.date, 
    s.start_time, 
    s.end_time, 
    p.location AS pool_location,
    CASE 
        WHEN l.session_type IS NOT NULL THEN 'Lesson'
        WHEN fs.session_id IS NOT NULL THEN 'Free Training'
        WHEN ot.swimming_style IS NOT NULL THEN 'One-to-One Training'
        ELSE 'Unknown'
    END AS session_type
FROM booking b
JOIN session s ON b.session_id = s.session_id
JOIN pool p ON s.pool_id = p.pool_id
LEFT JOIN lesson l ON s.session_id = l.session_id
LEFT JOIN freeSession fs ON s.session_id = fs.session_id
LEFT JOIN oneToOneTraining ot ON s.session_id = ot.session_id;

-- Trigger
DELIMITER $$

CREATE TRIGGER update_lesson_student_count_after_booking
AFTER INSERT ON booking
FOR EACH ROW
BEGIN
    UPDATE lesson
    SET student_count = student_count + 1
    WHERE session_id = NEW.session_id;
END$$

CREATE TRIGGER update_lesson_student_count_after_deletion
AFTER DELETE ON booking
FOR EACH ROW
BEGIN
    UPDATE lesson
    SET student_count = student_count - 1
    WHERE session_id = OLD.session_id;
END$$

DELIMITER ;

-- Mock Data
-- 1. Insert Pools
INSERT INTO pool (pool_id, location, chlorine_level) VALUES
(1, 'Downtown Indoor Pool', 1.50),
(2, 'Uptown Outdoor Pool', 1.20);

-- 2. Insert Lanes for Each Pool
-- Lanes for Pool 1 (Indoor)
INSERT INTO lane (pool_id, lane_no) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6);

-- Lanes for Pool 2 (Outdoor)
INSERT INTO lane (pool_id, lane_no) VALUES
(2, 1),
(2, 2),
(2, 3),
(2, 4),
(2, 5),
(2, 6);

-- 3. Insert Users and Their Related Data

-- 3.1 PoolAdmin User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(1, 'john-admin@example.com', 'password', 'John-Admin', 'Doe', 'Male', '1980-01-01');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(1, 60000.00, '2010-05-20');
INSERT INTO pool_admin (user_id, department) VALUES
(1, 'Operations');

-- 3.2 Coach User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(2, 'jane-coach@example.com', 'password', 'Jane-Coach', 'Smith', 'Female', '1985-02-15');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(2, 50000.00, '2012-07-10');
INSERT INTO coach (user_id, rank, specialization) VALUES
(2, 'Senior', 'Butterfly');

-- 3.3 Lifeguard User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(3, 'bob-lifeguard@example.com', 'password', 'Bob-Lifeguard', 'Brown', 'Male', '1990-03-25');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(3, 45000.00, '2015-09-01');
INSERT INTO lifeguard (user_id, license_no) VALUES
(3, 'LG12345');

-- 3.4 Employee User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(4, 'alice-employee@example.com', 'password', 'Alice-Employee', 'Davis', 'Female', '1992-04-30');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(4, 40000.00, '2018-11-15');

-- 3.5 Swimmer User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(5, 'charlie-swimmer@example.com', 'password', 'Charlie-Swimmer', 'Miller', 'Other', '2000-06-20');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(5, 'Intermediate');

-- 3.6 Member User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(6, 'diana-member@example.com', 'password', 'Diana-Member', 'Wilson', 'Female', '1995-07-10');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(6, 'Advanced');
INSERT INTO member (user_id, free_training_remaining) VALUES
(6, 5);

-- Insert Lessons (Session and Lesson Details)
-- Insert Sessions (3 in Pool 1 and 3 in Pool 2)
INSERT INTO session (session_id, description, pool_id, lane_no, date, start_time, end_time) VALUES
(1, 'Advanced swimming techniques', 1, 1, '2024-01-01', '09:00:00', '10:00:00'),
(2, 'Beginner swimming lesson', 1, 2, '2024-01-01', '09:30:00', '11:00:00'),
(3, 'Intermediate butterfly technique', 1, 3, '2024-01-03', '11:00:00', '12:00:00'),
(4, 'Personalized training for freestyle', 2, 1, '2024-01-04', '09:00:00', '10:00:00'),
(5, 'One-to-one backstroke training', 2, 2, '2024-01-05', '10:00:00', '11:00:00'),
(6, 'Advanced team lesson', 2, 3, '2024-01-06', '11:00:00', '12:00:00');

-- Assign Lesson or One-to-One Training types
-- Lesson sessions (Session IDs 1, 2, and 6)
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type) VALUES
(1, 2, 10, 15, 'Mixed'),
(2, 2, 8, 12, 'FemaleOnly'),
(6, 2, 15, 16, 'MaleOnly');

-- One-to-One Training sessions (Session IDs 3, 4, and 5)
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style) VALUES
(3, 2, 'Butterfly'),
(4, 2, 'Freestyle'),
(5, 2, 'Backstroke');

