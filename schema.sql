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
    price DECIMAL(10,2) DEFAULT 42,
    FOREIGN KEY (pool_id, lane_no) REFERENCES lane(pool_id, lane_no) ON DELETE CASCADE
);

-- 4.9 Booking Table
CREATE TABLE IF NOT EXISTS booking (
    swimmer_id INT NOT NULL,
    session_id INT NOT NULL,
    isCompleted BOOLEAN DEFAULT FALSE,
    paymentMethod ENUM('CreditCard', 'Cash') DEFAULT 'Cash',
    isPaymentCompleted BOOLEAN DEFAULT FALSE,
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
    student_count INT NOT NULL,
    capacity INT NOT NULL CHECK(capacity >= student_count),
    session_type ENUM('FemaleOnly', 'MaleOnly', 'Mixed') NOT NULL DEFAULT 'Mixed',
    price DECIMAL(10, 2) NOT NULL CHECK(price > 0),
    FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (coach_id) REFERENCES coach(user_id) ON DELETE CASCADE
);

-- 4.15 OneToOneTraining Table
CREATE TABLE IF NOT EXISTS oneToOneTraining (
    session_id INT PRIMARY KEY,
    coach_id INT NOT NULL,
    swimming_style VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK(price > 0),
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

-- 4.20 Admin Report Table
CREATE TABLE admin_report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_id INT NOT NULL,
    report_date DATETIME NOT NULL,
    number_of_swimmers INT, 
    number_of_lifeguards INT,
    most_liked_lesson VARCHAR(255),
    most_liked_coach VARCHAR(255),
    average_queue_length DECIMAL(10,2),
    FOREIGN KEY (admin_id) REFERENCES user(user_id)
);

-- 4.21 SwimmerWaitQueue Table
CREATE TABLE IF NOT EXISTS swimmerWaitQueue (
    swimmer_id INT NOT NULL,
    lesson_id INT NOT NULL,
    request_date DATE NOT NULL,
    PRIMARY KEY (swimmer_id, lesson_id),
    FOREIGN KEY (swimmer_id) REFERENCES member(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(session_id) ON DELETE CASCADE
);

-- Views
CREATE VIEW SessionsWithoutLifeguard AS
SELECT 
    s.session_id,
    s.description, 
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
    b.isCompleted,
    b.isPaymentCompleted,
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

-- Coach 2
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(8, 'michael-coach@example.com', 'password', 'Michael-Coach', 'Johnson', 'Male', '1983-08-12');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(8, 52000.00, '2013-06-01');
INSERT INTO coach (user_id, rank, specialization) VALUES
(8, 'Junior', 'Freestyle');

-- Coach 3
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(9, 'sarah-coach@example.com', 'password', 'Sarah-Coach', 'Williams', 'Female', '1987-11-22');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(9, 55000.00, '2014-09-15');
INSERT INTO coach (user_id, rank, specialization) VALUES
(9, 'Senior', 'Backstroke');

-- 3.3 Lifeguard User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(3, 'bob-lifeguard@example.com', 'password', 'Bob-Lifeguard', 'Brown', 'Male', '1990-03-25');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(3, 45000.00, '2015-09-01');
INSERT INTO lifeguard (user_id, license_no) VALUES
(3, 'LG12345');

-- Lifeguard 2
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(10, 'tom-lifeguard@example.com', 'password', 'Tom-Lifeguard', 'Taylor', 'Male', '1991-04-10');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(10, 47000.00, '2016-02-20');
INSERT INTO lifeguard (user_id, license_no) VALUES
(10, 'LG67890');

-- Lifeguard 3
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(11, 'linda-lifeguard@example.com', 'password', 'Linda-Lifeguard', 'Anderson', 'Female', '1993-07-05');
INSERT INTO employee (user_id, salary, emp_date) VALUES
(11, 48000.00, '2017-05-30');
INSERT INTO lifeguard (user_id, license_no) VALUES
(11, 'LG54321');

-- 3.5 Swimmer User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(5, 'charlie-swimmer@example.com', 'password', 'Charlie-Swimmer', 'Miller', 'Male', '2000-06-20');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(5, 'Intermediate');

-- 3.7 Swimmer
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(7, 'emily-swimmer@example.com', 'password', 'Emily-Swimmer', 'Miller', 'Female', '2000-06-20');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(7, 'Intermediate');

INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(12, 'george-swimmer@example.com', 'password', 'George-Swimmer', 'Thomas', 'Male', '2001-05-18');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(12, 'Beginner');

-- Swimmer 4
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(13, 'hannah-swimmer@example.com', 'password', 'Hannah-Swimmer', 'Martin', 'Female', '1999-09-30');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(13, 'Intermediate');

-- Swimmer 5
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(14, 'kevin-swimmer@example.com', 'password', 'Kevin-Swimmer', 'Lee', 'Male', '2002-12-12');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(14, 'Advanced');

-- 3.6 Member User
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(6, 'diana-member@example.com', 'password', 'Diana-Member', 'Wilson', 'Female', '1995-07-10');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(6, 'Advanced');
INSERT INTO member (user_id, free_training_remaining) VALUES
(6, 5);

INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(16, 'patrick-swimmer@example.com', 'password', 'Patrick-Swimmer', 'Martinez', 'Male', '2004-08-08');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(16, 'Beginner');

-- Swimmer 8
INSERT INTO user (user_id, email, password, forename, surname, gender, birth_date) VALUES
(17, 'sophia-swimmer@example.com', 'password', 'Sophia-Swimmer', 'Rodriguez', 'Female', '2005-02-14');
INSERT INTO swimmer (user_id, swimming_level) VALUES
(17, 'Advanced');

-- Swimmer 7 as Member
INSERT INTO member (user_id, free_training_remaining) VALUES
(16, 5);

-- Swimmer 8 as Member
INSERT INTO member (user_id, free_training_remaining) VALUES
(17, 5);


-- ###### END OF USERS INSERTION ######



-- #####################################################


-- Insert Lessons (Session and Lesson Details)
-- Insert Sessions (3 in Pool 1 and 3 in Pool 2)
-- Lesson 1: Mixed
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Advanced Mixed Lesson', 1, 1, '2024-12-05', '10:00:00', '11:30:00', 55.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 2, 10, 15, 'Mixed', 55.00);

-- Lesson 2: Female Only
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Female Only Lesson', 1, 2, '2024-12-12', '09:00:00', '10:30:00', 60.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 8, 10, 12, 'FemaleOnly', 60.00);

-- Lesson 3: Male Only
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Male Only Lesson', 2, 1, '2024-12-20', '14:00:00', '15:30:00', 65.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 9, 12, 14, 'MaleOnly', 65.00);

-- Lesson 4: Mixed Evening
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Mixed Lesson Evening', 2, 2, '2024-12-28', '18:00:00', '19:30:00', 55.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 2, 13, 15, 'Mixed', 55.00);

-- Insert Lessons in February 2025

-- Lesson 5: Advanced Butterfly
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Advanced Butterfly Lesson', 1, 3, '2025-02-03', '08:00:00', '09:30:00', 70.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 8, 10, 15, 'Mixed', 70.00);

-- Lesson 6: Freestyle Improvement
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Freestyle Improvement', 2, 3, '2025-02-07', '10:00:00', '11:30:00', 60.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 9, 11, 12, 'Mixed', 60.00);

-- Lesson 7: Beginner Mixed
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Beginner Mixed Lesson', 1, 4, '2025-02-10', '13:00:00', '14:30:00', 50.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 2, 9, 15, 'Mixed', 50.00);

-- Lesson 8: Intermediate Female
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Intermediate Female Lesson', 2, 4, '2025-02-14', '15:00:00', '16:30:00', 60.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 8, 12, 12, 'FemaleOnly', 60.00);

-- Lesson 9: Male Only Morning
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Male Only Morning Lesson', 1, 5, '2025-02-18', '07:00:00', '08:30:00', 65.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 9, 13, 14, 'MaleOnly', 65.00);

-- Lesson 10: Mixed Afternoon
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Mixed Lesson Afternoon', 2, 5, '2025-02-22', '14:00:00', '15:30:00', 55.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 2, 14, 15, 'Mixed', 55.00);

-- Lesson 11: Advanced Backstroke
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Advanced Backstroke', 1, 6, '2025-02-25', '16:00:00', '17:30:00', 70.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 8, 10, 15, 'Mixed', 70.00);

-- Lesson 12: Freestyle Mastery
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('Freestyle Mastery', 2, 6, '2025-02-28', '18:00:00', '19:30:00', 60.00);
INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
VALUES (LAST_INSERT_ID(), 9, 11, 12, 'Mixed', 60.00);

-- OneToOneTraining 1 (December 2024)
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('One-to-One Butterfly Training', 1, 1, '2024-12-10', '11:00:00', '12:00:00', 100.00);
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
VALUES (LAST_INSERT_ID(), 2, 'Butterfly', 100.00);

-- OneToOneTraining 2 (December 2024)
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('One-to-One Freestyle Training', 2, 1, '2024-12-20', '13:00:00', '14:00:00', 90.00);
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
VALUES (LAST_INSERT_ID(), 8, 'Freestyle', 90.00);

-- OneToOneTraining 3 (February 2025)
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('One-to-One Backstroke Training', 1, 2, '2025-02-05', '10:00:00', '11:00:00', 80.00);
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
VALUES (LAST_INSERT_ID(), 9, 'Backstroke', 80.00);

-- OneToOneTraining 4 (February 2025)
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('One-to-One Breaststroke Training', 2, 2, '2025-02-12', '12:00:00', '13:00:00', 85.00);
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
VALUES (LAST_INSERT_ID(), 2, 'Breaststroke', 85.00);

-- OneToOneTraining 5 (February 2025)
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('One-to-One Mixed Style Training', 1, 3, '2025-02-20', '14:00:00', '15:00:00', 95.00);
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
VALUES (LAST_INSERT_ID(), 8, 'Mixed', 95.00);

-- OneToOneTraining 6 (February 2025)
INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time, price)
VALUES ('One-to-One Advanced Freestyle', 2, 3, '2025-02-25', '16:00:00', '17:00:00', 100.00);
INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
VALUES (LAST_INSERT_ID(), 9, 'Freestyle', 100.00);

INSERT INTO booking (swimmer_id, session_id, isCompleted, isPaymentCompleted)
SELECT 
    6 AS swimmer_id, 
    s.session_id, 
    TRUE AS isCompleted, 
    TRUE AS isPaymentCompleted
FROM 
    session s
WHERE 
    s.date BETWEEN '2024-01-01' AND '2024-12-31';