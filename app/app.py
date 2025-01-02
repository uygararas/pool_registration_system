from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353project'

mysql = MySQL(app)

def get_user_role(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Check for Admin (PoolAdmin)
    cursor.execute('SELECT * FROM pool_admin WHERE user_id = %s', (user_id,))
    if cursor.fetchone():
        return 'Admin'
    
    # Check for Coach
    cursor.execute('SELECT * FROM coach WHERE user_id = %s', (user_id,))
    if cursor.fetchone():
        return 'Coach'
    
    # Check for Lifeguard
    cursor.execute('SELECT * FROM lifeguard WHERE user_id = %s', (user_id,))
    if cursor.fetchone():
        return 'Lifeguard'
    
    # Check for Member
    cursor.execute('SELECT * FROM member WHERE user_id = %s', (user_id,))
    if cursor.fetchone():
        return 'Member'
    
    # Default role
    return 'Swimmer'


@app.route('/test')
def test():
    print("test")
    return "Server is running"

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('homepage'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and all(k in request.form for k in ['email', 'password']):
        email = request.form['email']
        password = request.form['password'] 
        forename = request.form['forename']
        surname = request.form['surname']
        gender = request.form['gender']
        birth_date = request.form['birth_date']
        role = request.form['role']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if user already exists
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            flash('Account already exists!', 'danger')
            return render_template('register.html')
        else:
            # Insert into user table
            cursor.execute('INSERT INTO user (email, password, forename, surname, gender, birth_date) VALUES (%s, %s, %s, %s, %s, %s)',
                           (email, password, forename, surname, gender, birth_date))
            mysql.connection.commit()

            # Get the newly created user_id
            cursor.execute('SELECT user_id FROM user WHERE email = %s', (email,))
            user = cursor.fetchone()
            user_id = user['user_id']

            # Depending on role, insert into respective tables
            if role == 'Employee':
                salary = request.form.get('salary')
                emp_date = request.form.get('emp_date')
                cursor.execute('INSERT INTO employee (user_id, salary, emp_date) VALUES (%s, %s, %s)',
                               (user_id, salary, emp_date))
                mysql.connection.commit()

            elif role == 'PoolAdmin':
                # PoolAdmin is a type of Employee
                salary = request.form.get('salary')
                emp_date = request.form.get('emp_date')
                department = request.form.get('department')
                cursor.execute('INSERT INTO employee (user_id, salary, emp_date) VALUES (%s, %s, %s)',
                               (user_id, salary, emp_date))
                cursor.execute('INSERT INTO pool_admin (user_id, department) VALUES (%s, %s)',
                               (user_id, department))
                mysql.connection.commit()

            elif role == 'Lifeguard':
                salary = request.form.get('salary')
                emp_date = request.form.get('emp_date')
                license_no = request.form.get('license_no')
                cursor.execute('INSERT INTO employee (user_id, salary, emp_date) VALUES (%s, %s, %s)',
                               (user_id, salary, emp_date))
                cursor.execute('INSERT INTO lifeguard (user_id, license_no) VALUES (%s, %s)',
                               (user_id, license_no))
                mysql.connection.commit()

            elif role == 'Coach':
                salary = request.form.get('salary')
                emp_date = request.form.get('emp_date')
                rank = request.form.get('rank')
                specialization = request.form.get('specialization')
                cursor.execute('INSERT INTO employee (user_id, salary, emp_date) VALUES (%s, %s, %s)',
                               (user_id, salary, emp_date))
                cursor.execute('INSERT INTO coach (user_id, rank, specialization) VALUES (%s, %s, %s)',
                               (user_id, rank, specialization))
                mysql.connection.commit()

            elif role == 'Swimmer':
                swimming_level = request.form.get('swimming_level')
                cursor.execute('INSERT INTO swimmer (user_id, swimming_level) VALUES (%s, %s)',
                               (user_id, swimming_level))
                mysql.connection.commit()

            elif role == 'Member':
                # Member is a type of Swimmer
                swimming_level = request.form.get('swimming_level')
                free_training_remaining = request.form.get('free_training_remaining', 0)
                cursor.execute('INSERT INTO swimmer (user_id, swimming_level) VALUES (%s, %s)',
                               (user_id, swimming_level))
                cursor.execute('INSERT INTO member (user_id, free_training_remaining) VALUES (%s, %s)',
                               (user_id, free_training_remaining))
                mysql.connection.commit()

            flash('You have successfully registered!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and all(k in request.form for k in ['email', 'password']):
        email = request.form['email']
        password = request.form['password'] 
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account and account['password'] == password:
            # User exists and password is correct
            user_id = account['user_id']
            role = get_user_role(user_id)  # Determine the user's role
            
            session['loggedin'] = True
            session['user_id'] = user_id
            session['email'] = account['email']
            session['forename'] = account['forename']
            session['surname'] = account['surname']
            session['gender'] = account['gender']
            session['role'] = role  # Store role in session
            flash('Logged in successfully as {}!'.format(role), 'success')
            return redirect(url_for('homepage'))
        else:
            flash('Incorrect email/password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove session data
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('forename', None)
    session.pop('surname', None)
    session.pop('role', None)
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

@app.route('/homepage')
def homepage():
    if 'loggedin' in session:
        role = session.get('role', 'Swimmer')
        if role == 'Admin':
            return redirect(url_for('admin_homepage'))
        elif role == 'Coach':
            return redirect(url_for('coach_homepage'))
        elif role == 'Lifeguard':
            return redirect(url_for('lifeguard_homepage'))
        elif role == 'Member' or role == 'Swimmer':
            return redirect(url_for('swimmer_homepage'))
        else:
            forename = session.get('forename', 'User')
            return render_template('homepage.html', forename=forename)

    return redirect(url_for('login'))


#################################################################
#### LIFEGUARD FUNCTIONS ########################################
#################################################################

@app.route('/lifeguard_homepage')
def lifeguard_homepage():
    if 'loggedin' in session and session.get('role') == 'Lifeguard':
        forename = session.get('forename', 'Lifeguard')
        lifeguard_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch sessions without lifeguard, sorted by start_time ascending
        cursor.execute('SELECT * FROM SessionsWithoutLifeguard ORDER BY date ASC, start_time ASC')
        sessions_without_lifeguard = cursor.fetchall()

        # Fetch sessions assigned to this lifeguard, sorted by start_time ascending
        cursor.execute("""
        SELECT s.*, p.location AS pool_location
        FROM session s
        JOIN guards g ON s.session_id = g.session_id
        JOIN pool p ON s.pool_id = p.pool_id
        WHERE g.lifeguard_id = %s
            ORDER BY s.date ASC, s.start_time ASC
            """, (lifeguard_id,))
        assigned_sessions = cursor.fetchall()

        
        return render_template('lifeguard_homepage.html', forename=forename,
                               sessions_without_lifeguard=sessions_without_lifeguard,
                               assigned_sessions=assigned_sessions)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/assign_session/<int:session_id>', methods=['POST'])
def assign_session(session_id):
    if 'loggedin' in session and session.get('role') == 'Lifeguard':
        lifeguard_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if the session is still without a lifeguard
        cursor.execute('SELECT * FROM SessionsWithoutLifeguard WHERE session_id = %s', (session_id,))
        session_data = cursor.fetchone()
        
        if session_data:
            try:
                # Assign the lifeguard to the session
                cursor.execute('INSERT INTO guards (lifeguard_id, session_id) VALUES (%s, %s)', (lifeguard_id, session_id))
                mysql.connection.commit()
                flash(f'Successfully assigned to session ID {session_id}.', 'success')
            except MySQLdb.IntegrityError:
                mysql.connection.rollback()
                flash('Failed to assign to session. It might have been assigned already.', 'danger')
        else:
            flash('Session not available for assignment.', 'warning')
        
        return redirect(url_for('lifeguard_homepage'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/drop_session_lifeguard/<int:session_id>', methods=['POST'])
def drop_session_lifeguard(session_id):
    if 'loggedin' in session and session.get('role') == 'Lifeguard':
        lifeguard_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if the lifeguard is assigned to the session
        cursor.execute('SELECT * FROM guards WHERE session_id = %s AND lifeguard_id = %s', (session_id, lifeguard_id))
        assignment = cursor.fetchone()
        
        if assignment:
            try:
                # Remove the assignment
                cursor.execute('DELETE FROM guards WHERE session_id = %s AND lifeguard_id = %s', (session_id, lifeguard_id))
                mysql.connection.commit()
                flash(f'Successfully dropped session ID {session_id}.', 'success')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error dropping session: {str(e)}', 'danger')
        else:
            flash('You are not assigned to this session.', 'warning')
        
        return redirect(url_for('lifeguard_homepage'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
# end of lifeguard functions

#################################################################
#### SWIMMER/MEMBER FUNCTIONS ###################################
#################################################################

@app.route('/swimmer_homepage')
def swimmer_homepage():
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        forename = session.get('forename', 'DefaultForename')
        swimmer_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch upcoming sessions
        cursor.execute("""
            SELECT 
                session_id, 
                description, 
                date, 
                start_time, 
                end_time, 
                pool_location,
                session_type,
                isPaymentCompleted
            FROM swimmer_booked_sessions
            WHERE swimmer_id = %s AND isCompleted = FALSE
            ORDER BY date ASC, start_time ASC
        """, (swimmer_id,))
        upcoming_sessions = cursor.fetchall()
        
        # Fetch completed sessions
        cursor.execute("""
            SELECT 
                session_id, 
                description, 
                date, 
                start_time, 
                end_time, 
                pool_location,
                session_type,
                isPaymentCompleted
            FROM swimmer_booked_sessions
            WHERE swimmer_id = %s AND isCompleted = TRUE
            ORDER BY date DESC, start_time DESC
        """, (swimmer_id,))
        completed_sessions = cursor.fetchall()

        # Enhance completed_sessions with review flags
        for session_item in completed_sessions:
            session_id = session_item['session_id']
            session_type = session_item['session_type']
            
            # Initialize flags
            session_item['has_reviewed_coach'] = False
            session_item['has_reviewed_lesson'] = False
            
            if session_type in ['Lesson', 'One-to-One Training']:
                # Fetch coach_id for the session
                if session_type == 'Lesson':
                    cursor.execute("""
                        SELECT coach_id FROM lesson WHERE session_id = %s
                    """, (session_id,))
                    coach = cursor.fetchone()
                elif session_type == 'One-to-One Training':
                    cursor.execute("""
                        SELECT coach_id FROM oneToOneTraining WHERE session_id = %s
                    """, (session_id,))
                    coach = cursor.fetchone()
                
                coach_id = coach['coach_id'] if coach else None
                
                if coach_id:
                    # Check if coach has been reviewed
                    cursor.execute("""
                        SELECT cr.review_id
                        FROM coachReview cr
                        JOIN review r ON cr.review_id = r.review_id
                        WHERE cr.coach_id = %s AND r.user_id = %s
                    """, (coach_id, swimmer_id))
                    coach_review = cursor.fetchone()
                    session_item['has_reviewed_coach'] = True if coach_review else False
                
                if session_type == 'Lesson':
                    # Check if lesson has been reviewed
                    cursor.execute("""
                        SELECT lr.review_id
                        FROM lessonReview lr
                        JOIN review r ON lr.review_id = r.review_id
                        WHERE lr.lesson_id = %s AND r.user_id = %s
                    """, (session_id, swimmer_id))
                    lesson_review = cursor.fetchone()
                    session_item['has_reviewed_lesson'] = True if lesson_review else False

        cursor.close()
        
        return render_template('swimmer_homepage.html', 
                               forename=forename, 
                               upcoming_sessions=upcoming_sessions, 
                               completed_sessions=completed_sessions)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
@app.route('/review_coach/<int:session_id>', methods=['GET', 'POST'])
def review_coach(session_id):
    if 'loggedin' not in session or session.get('role') not in ['Member', 'Swimmer']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    swimmer_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Verify participation
    cursor.execute("""
        SELECT s.session_type, l.coach_id
        FROM swimmer_booked_sessions s
        LEFT JOIN lesson l ON s.session_id = l.session_id
        LEFT JOIN oneToOneTraining ot ON s.session_id = ot.session_id
        WHERE s.session_id = %s AND s.swimmer_id = %s AND s.isCompleted = TRUE
    """, (session_id, swimmer_id))
    session_info = cursor.fetchone()
    
    if not session_info:
        flash('Session not found or not completed.', 'danger')
        cursor.close()
        return redirect(url_for('swimmer_homepage'))
    
    coach_id = session_info.get('coach_id')
    if not coach_id:
        flash('Coach not found for this session.', 'danger')
        cursor.close()
        return redirect(url_for('swimmer_homepage'))
    
    # Check if already reviewed
    cursor.execute("""
        SELECT cr.review_id
        FROM coachReview cr
        JOIN review r ON cr.review_id = r.review_id
        WHERE cr.coach_id = %s AND r.user_id = %s
    """, (coach_id, swimmer_id))
    existing_review = cursor.fetchone()
    
    if existing_review:
        flash('You have already reviewed this coach for this session.', 'info')
        cursor.close()
        return redirect(url_for('swimmer_homepage'))
    
    if request.method == 'POST':
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        
        # Input validation
        if not comment or not rating:
            flash('Please provide both comment and rating.', 'warning')
            cursor.close()
            return render_template('swimmer_review_coach.html', session_id=session_id)
        
        try:
            rating = float(rating)
            if rating < 0 or rating > 5:
                raise ValueError
        except ValueError:
            flash('Rating must be a number between 0 and 5.', 'warning')
            cursor.close()
            return render_template('swimmer_review_coach.html', session_id=session_id)
        
        try:
            # Insert into review table
            cursor.execute("""
                INSERT INTO review (user_id, comment, rating) VALUES (%s, %s, %s)
            """, (swimmer_id, comment, rating))
            review_id = cursor.lastrowid
            
            # Insert into coachReview table
            cursor.execute("""
                INSERT INTO coachReview (review_id, coach_id) VALUES (%s, %s)
            """, (review_id, coach_id))
            
            mysql.connection.commit()
            flash('Coach reviewed successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error submitting review: {str(e)}', 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('swimmer_homepage'))
    
    cursor.close()
    return render_template('swimmer_review_coach.html', session_id=session_id)


@app.route('/review_lesson/<int:session_id>', methods=['GET', 'POST'])
def review_lesson(session_id):
    if 'loggedin' not in session or session.get('role') not in ['Member', 'Swimmer']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    swimmer_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Verify participation
    cursor.execute("""
        SELECT session_type
        FROM swimmer_booked_sessions
        WHERE session_id = %s AND swimmer_id = %s AND isCompleted = TRUE
    """, (session_id, swimmer_id))
    session_info = cursor.fetchone()
    
    if not session_info or session_info['session_type'] != 'Lesson':
        flash('Session not found, not completed, or not a lesson.', 'danger')
        cursor.close()
        return redirect(url_for('swimmer_homepage'))
    
    # Check if already reviewed
    cursor.execute("""
        SELECT lr.review_id
        FROM lessonReview lr
        JOIN review r ON lr.review_id = r.review_id
        WHERE lr.lesson_id = %s AND r.user_id = %s
    """, (session_id, swimmer_id))
    existing_review = cursor.fetchone()
    
    if existing_review:
        flash('You have already reviewed this lesson.', 'info')
        cursor.close()
        return redirect(url_for('swimmer_homepage'))
    
    if request.method == 'POST':
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        
        # Input validation
        if not comment or not rating:
            flash('Please provide both comment and rating.', 'warning')
            cursor.close()
            return render_template('swimmer_review_lesson.html', session_id=session_id)
        
        try:
            rating = float(rating)
            if rating < 0 or rating > 5:
                raise ValueError
        except ValueError:
            flash('Rating must be a number between 0 and 5.', 'warning')
            cursor.close()
            return render_template('swimmer_review_lesson.html', session_id=session_id)
        
        try:
            # Insert into review table
            cursor.execute("""
                INSERT INTO review (user_id, comment, rating) VALUES (%s, %s, %s)
            """, (swimmer_id, comment, rating))
            review_id = cursor.lastrowid
            
            # Insert into lessonReview table
            cursor.execute("""
                INSERT INTO lessonReview (review_id, lesson_id) VALUES (%s, %s)
            """, (review_id, session_id))
            
            mysql.connection.commit()
            flash('Lesson reviewed successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error submitting review: {str(e)}', 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('swimmer_homepage'))
    
    cursor.close()
    return render_template('swimmer_review_lesson.html', session_id=session_id)
    
@app.route('/swimmer_lessons')
def swimmer_lessons():
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        forename = session.get('forename', 'Member')
        swimmer_id = session['user_id']
        role = session.get('role')

        # Retrieve filter parameters
        class_date = request.args.get('class_date')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        pool_id = request.args.get('pool_id')
        session_type = request.args.get('session_type')
        coach_id = request.args.get('coach_id')
        min_capacity = request.args.get('min_capacity')
        max_capacity = request.args.get('max_capacity')

        # Updated SQL query to include session price
        query = """
            SELECT 
                s.session_id, 
                s.description, 
                s.date, 
                s.start_time, 
                s.end_time, 
                p.location AS pool_location,
                l.session_type,
                l.capacity,
                l.student_count,
                s.price,
                c.forename AS coach_forename,
                c.surname AS coach_surname,
                EXISTS (
                    SELECT 1 FROM booking b 
                    WHERE b.session_id = s.session_id AND b.swimmer_id = %s
                ) AS is_enrolled
            FROM session s
            JOIN pool p ON s.pool_id = p.pool_id
            JOIN lesson l ON s.session_id = l.session_id
            JOIN coach co ON l.coach_id = co.user_id
            JOIN user c ON co.user_id = c.user_id
            WHERE 1=1
        """
        params = [swimmer_id]

        # Apply filters if provided
        if class_date:
            query += " AND s.date = %s"
            params.append(class_date)
        if start_time:
            query += " AND s.start_time >= %s"
            params.append(start_time)
        if end_time:
            query += " AND s.end_time <= %s"
            params.append(end_time)
        if pool_id and pool_id != 'All':
            query += " AND p.pool_id = %s"
            params.append(pool_id)
        if session_type and session_type != 'All':
            query += " AND l.session_type = %s"
            params.append(session_type)
        if coach_id and coach_id != 'All':
            query += " AND co.user_id = %s"
            params.append(coach_id)
        if min_capacity:
            query += " AND l.capacity >= %s"
            params.append(min_capacity)
        if max_capacity:
            query += " AND l.capacity <= %s"
            params.append(max_capacity)

        query += " ORDER BY s.date ASC, s.start_time ASC"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, tuple(params))
        lessons = cursor.fetchall()

        # Fetch available pools for the filter dropdown
        cursor.execute("SELECT pool_id, location FROM pool")
        pools = cursor.fetchall()

        # Fetch available coaches for the filter dropdown
        cursor.execute("""
            SELECT c.user_id, u.forename, u.surname 
            FROM coach c
            JOIN user u ON c.user_id = u.user_id
        """)
        coaches = cursor.fetchall()

        # Fetch distinct session types
        cursor.execute("SELECT DISTINCT session_type FROM lesson")
        session_types = [row['session_type'] for row in cursor.fetchall()]

        # Check if user is already in the queue for each lesson
        for lesson in lessons:
            # Check if user is in the queue
            cursor.execute('SELECT * FROM swimmerWaitQueue WHERE swimmer_id = %s AND lesson_id = %s', (swimmer_id, lesson['session_id']))
            queue = cursor.fetchone()
            lesson['is_in_queue'] = True if queue else False

            # Determine if the user can join the queue
            if lesson['student_count'] >= lesson['capacity'] and role == 'Member':
                lesson['can_join_queue'] = True
            else:
                lesson['can_join_queue'] = False

        cursor.close()

        return render_template('swimmer_lesson.html', 
                               forename=forename, 
                               lessons=lessons,
                               pools=pools,
                               coaches=coaches,
                               session_types=session_types,
                               filters=request.args)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/swimmer_lesson_enroll_payment/<int:session_id>', methods=['GET'])
def swimmer_lesson_enroll_payment(session_id):
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        return render_template('swimmer_lesson_enroll_payment.html', session_id=session_id)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

# Add this new route or modify the existing enroll_lesson route

@app.route('/enroll_lesson/<int:session_id>', methods=['POST'])
def enroll_lesson(session_id):
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        swimmer_id = session['user_id']
        user_gender = session['gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if already enrolled
        cursor.execute('SELECT * FROM booking WHERE swimmer_id = %s AND session_id = %s', (swimmer_id, session_id))
        enrollment = cursor.fetchone()
        
        if enrollment:
            flash('You are already enrolled in this lesson.', 'warning')
            return redirect(url_for('swimmer_lessons'))
        
        # Fetch desired session details
        cursor.execute('SELECT s.date, s.start_time, s.end_time FROM session s WHERE s.session_id = %s', (session_id,))
        desired_session = cursor.fetchone()
        
        if not desired_session:
            flash('Session not found.', 'danger')
            return redirect(url_for('swimmer_lessons'))
        
        desired_date = desired_session['date']
        desired_start = desired_session['start_time']
        desired_end = desired_session['end_time']

        # Fetch all sessions the swimmer is currently enrolled in
        cursor.execute("""
            SELECT s.date, s.start_time, s.end_time
            FROM booking b
            JOIN session s ON b.session_id = s.session_id
            WHERE b.swimmer_id = %s
        """, (swimmer_id,))
        enrolled_sessions = cursor.fetchall()
        
        # Check for overlapping sessions
        for sess in enrolled_sessions:
            if sess['date'] != desired_date:
                continue  # Different dates, no conflict
            # Check if times overlap
            if not (desired_end <= sess['start_time'] or desired_start >= sess['end_time']):
                flash('Enrollment failed: You are already enrolled in another session that overlaps with this time slot.', 'danger')
                return redirect(url_for('swimmer_lessons'))
            
        # Check if the restrictions are satisfied
        cursor.execute('SELECT capacity, student_count, session_type FROM lesson WHERE session_id = %s', (session_id,))
        lesson = cursor.fetchone()

        if not lesson:
            flash('Lesson details not found.', 'danger')
            return redirect(url_for('swimmer_lessons'))
        
        lesson_type = lesson['session_type']
        if (lesson_type == 'FemaleOnly' and user_gender != 'Female') or (lesson_type == 'MaleOnly' and user_gender != 'Male'):
            flash(f'This lesson is restricted to {lesson_type}. Your gender: {user_gender} does not match the requirement.', 'warning')
            return redirect(url_for('swimmer_lessons'))
        
        if lesson['student_count'] >= lesson['capacity']:
            flash('Cannot enroll: The lesson is full.', 'danger')
            return redirect(url_for('swimmer_lessons'))
        
        # Insert the booking with isCompleted=False and isPaymentCompleted=False
        try:
            cursor.execute('INSERT INTO booking (swimmer_id, session_id, isCompleted, isPaymentCompleted) VALUES (%s, %s, %s, %s)',
                           (swimmer_id, session_id, False, False))
            mysql.connection.commit()
            flash('Successfully enrolled in the lesson. Please proceed to payment.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error enrolling in lesson: {str(e)}', 'danger')
            return redirect(url_for('swimmer_lessons'))
        
        return redirect(url_for('swimmer_lesson_enroll_payment', session_id=session_id))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/process_payment/<int:session_id>', methods=['POST'])
def process_payment(session_id):
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        swimmer_id = session['user_id']
        payment_method = request.form.get('payment_method')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Validate payment method
        if payment_method not in ['CreditCard', 'Cash']:
            flash('Invalid payment method selected.', 'danger')
            return redirect(url_for('swimmer_lesson_enroll_payment', session_id=session_id))
        
        # Update the booking
        try:
            if payment_method == 'CreditCard':
                # Assume payment is successful
                is_payment_completed = True
            else:
                is_payment_completed = False
            
            # Update the booking
            cursor.execute("""
                UPDATE booking 
                SET paymentMethod = %s, isPaymentCompleted = %s 
                WHERE swimmer_id = %s AND session_id = %s
            """, (payment_method, is_payment_completed, swimmer_id, session_id))
            
            mysql.connection.commit()
            
            if is_payment_completed:
                flash('Payment successful and enrollment completed!', 'success')
            else:
                flash('Enrollment created. Please complete the payment later.', 'info')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error processing payment: {str(e)}', 'danger')
            return redirect(url_for('swimmer_lesson_enroll_payment', session_id=session_id))
        
        return redirect(url_for('swimmer_homepage'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/exit_lesson/<int:session_id>', methods=['POST'])
def exit_lesson(session_id):
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        swimmer_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if enrolled
        cursor.execute('SELECT * FROM booking WHERE swimmer_id = %s AND session_id = %s', (swimmer_id, session_id))
        enrollment = cursor.fetchone()
        
        if not enrollment:
            flash('You are not enrolled in this lesson.', 'warning')
            return redirect(url_for('swimmer_lessons'))
        
        # Exit the lesson
        try:
            cursor.execute('DELETE FROM booking WHERE swimmer_id = %s AND session_id = %s', (swimmer_id, session_id))
            
            # Handle wait queue
            cursor.execute("""
                SELECT swimmer_id FROM swimmerWaitQueue
                WHERE lesson_id = %s
                ORDER BY request_date ASC
                LIMIT 1
            """, (session_id,))
            next_swimmer = cursor.fetchone()
            
            if next_swimmer:
                next_swimmer_id = next_swimmer['swimmer_id']
                # Enroll the next swimmer
                cursor.execute('INSERT INTO booking (swimmer_id, session_id, isCompleted, paymentMethod, isPaymentCompleted) VALUES (%s, %s, FALSE, "Cash", FALSE)', (next_swimmer_id, session_id))
                # Remove from wait queue
                cursor.execute('DELETE FROM swimmerWaitQueue WHERE swimmer_id = %s AND lesson_id = %s', (next_swimmer_id, session_id))
                
            mysql.connection.commit()
            flash('Successfully exited the lesson.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error exiting lesson: {str(e)}', 'danger')
        
        return redirect(url_for('swimmer_lessons'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))


@app.route('/join_queue/<int:session_id>', methods=['POST'])
def join_queue(session_id):
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        swimmer_id = session['user_id']
        role = session.get('role')

        if role != 'Member':
            flash('Only members can join the queue.', 'warning')
            return redirect(url_for('swimmer_lessons'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Check if already in queue
            cursor.execute('SELECT * FROM swimmerWaitQueue WHERE swimmer_id = %s AND lesson_id = %s', (swimmer_id, session_id))
            if cursor.fetchone():
                flash('You are already in the queue for this lesson.', 'info')
                return redirect(url_for('swimmer_lessons'))

            # Insert into swimmerWaitQueue
            current_date = datetime.today().date()
            cursor.execute('INSERT INTO swimmerWaitQueue (swimmer_id, lesson_id, request_date) VALUES (%s, %s, %s)', (swimmer_id, session_id, current_date))
            mysql.connection.commit()
            flash('Successfully joined the queue for the lesson.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error joining queue: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('swimmer_lessons'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/quit_queue/<int:session_id>', methods=['POST'])
def quit_queue(session_id):
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        swimmer_id = session['user_id']
        role = session.get('role')

        if role != 'Member':
            flash('Only members can quit the queue.', 'warning')
            return redirect(url_for('swimmer_lessons'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Check if in queue
            cursor.execute('SELECT * FROM swimmerWaitQueue WHERE swimmer_id = %s AND lesson_id = %s', (swimmer_id, session_id))
            if not cursor.fetchone():
                flash('You are not in the queue for this lesson.', 'info')
                return redirect(url_for('swimmer_lessons'))

            # Delete from swimmerWaitQueue
            cursor.execute('DELETE FROM swimmerWaitQueue WHERE swimmer_id = %s AND lesson_id = %s', (swimmer_id, session_id))
            mysql.connection.commit()
            flash('Successfully quit the queue for the lesson.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error quitting queue: {str(e)}', 'danger')
        finally:
            cursor.close()
        return redirect(url_for('swimmer_lessons'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/swimmer_free_session')
def swimmer_free_session():
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        forename = session.get('forename', 'Member')
        return render_template('swimmer_free_session.html', forename=forename)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/swimmer_one_to_one_training')
def swimmer_one_to_one_training():
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        forename = session.get('forename', 'Member')
        return render_template('swimmer_one_to_one_training.html', forename=forename)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
#end of swimmer/member functions

#################################################################
#### COACH FUNCTIONS ############################################
#################################################################

@app.route('/coach_homepage')
def coach_homepage():
    if 'loggedin' in session and session.get('role') == 'Coach':
        forename = session.get('forename', 'Coach')
        coach_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch Lessons (General Classes)
        cursor.execute("""
            SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, 
                   s.pool_id, s.lane_no, l.session_type, l.price
            FROM lesson l
            JOIN session s ON l.session_id = s.session_id
            WHERE l.coach_id = %s
        """, (coach_id,))
        lessons = cursor.fetchall()

        # Fetch One-to-One Trainings
        cursor.execute("""
            SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, 
                   s.pool_id, s.lane_no, o.swimming_style, o.price
            FROM oneToOneTraining o
            JOIN session s ON o.session_id = s.session_id
            WHERE o.coach_id = %s
        """, (coach_id,))
        one_to_one_trainings = cursor.fetchall()

        # Get the current date and time
        current_date = datetime.now().date()
        current_time = datetime.now().time()

        return render_template(
            'coach_homepage.html',
            forename=forename,
            lessons=lessons,
            one_to_one_trainings=one_to_one_trainings,
            current_date=current_date,
            current_time=current_time
        )
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/create_lesson', methods=['GET', 'POST'])
def create_lesson():
    if 'loggedin' in session and session.get('role') == 'Coach':
        if request.method == 'POST':
            description = request.form['description']
            class_date = request.form['class_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            pool_id = request.form['pool_id']
            lane_no = request.form['lane_no']
            capacity = request.form['capacity']
            session_type = request.form['session_type']
            price = request.form['price']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Validate Pool and Lane
            cursor.execute("""
                SELECT * FROM session 
                WHERE pool_id = %s AND lane_no = %s AND date = %s
                  AND (
                      (start_time < %s AND end_time > %s) OR
                      (start_time < %s AND end_time > %s) OR
                      (start_time >= %s AND end_time <= %s)
                  )
            """, (pool_id, lane_no, class_date, end_time, start_time, end_time, start_time, start_time, end_time))
            conflict = cursor.fetchone()
            
            if conflict:
                flash('Conflict detected: Another session overlaps with the selected time and lane.', 'danger')
                return redirect(url_for('create_lesson'))
            
            # Check for coach schedule conflict
            coach_id = session['user_id']
            cursor.execute("""
                SELECT * FROM session s
                JOIN lesson l ON s.session_id = l.session_id
                WHERE l.coach_id = %s AND s.date = %s
                  AND (
                      (s.start_time < %s AND s.end_time > %s) OR
                      (s.start_time < %s AND s.end_time > %s) OR
                      (s.start_time >= %s AND s.end_time <= %s)
                  )
            """, (coach_id, class_date, end_time, start_time, end_time, start_time, start_time, end_time))
            coach_conflict = cursor.fetchone()
            
            if coach_conflict:
                flash('You already have a lesson scheduled during this time.', 'danger')
                return redirect(url_for('create_lesson'))
            
            # Check for conflicts with one-to-one trainings
            cursor.execute("""
                SELECT * FROM session s
                JOIN oneToOneTraining o ON s.session_id = o.session_id
                WHERE o.coach_id = %s AND s.date = %s
                AND (
                    (s.start_time < %s AND s.end_time > %s) OR
                    (s.start_time >= %s AND s.end_time <= %s)
                )
            """, (coach_id, class_date, end_time, start_time, start_time, end_time))
            training_conflict = cursor.fetchone()

            if training_conflict:
                flash('Conflict detected: You already have a one-to-one training scheduled during this time.', 'danger')
                return redirect(url_for('create_lesson'))

            # Insert into session table
            try:
                cursor.execute("""
                    INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (description, pool_id, lane_no, class_date, start_time, end_time))
                mysql.connection.commit()
                session_id = cursor.lastrowid  # Get the generated session_id
            except Exception as e:
                mysql.connection.rollback()
                flash('Error creating session: {}'.format(str(e)), 'danger')
                return redirect(url_for('create_lesson'))
            
            # Insert into lesson table
            try:
                cursor.execute("""
                    INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type, price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (session_id, coach_id, 0, capacity, session_type, price))
                mysql.connection.commit()
            except Exception as e:
                mysql.connection.rollback()
                flash('Error creating lesson: {}'.format(str(e)), 'danger')
                return redirect(url_for('create_lesson'))
            
            flash('Lesson created and published successfully!', 'success')
            return redirect(url_for('homepage'))
        
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
                SELECT pool.pool_id, pool.location, pool.chlorine_level, COUNT(lane.lane_no) AS lane_count
                FROM pool
                JOIN lane ON pool.pool_id = lane.pool_id
                GROUP BY pool.pool_id, pool.location, pool.chlorine_level
            """)
            pools = cursor.fetchall()

            return render_template('create_lesson.html', pools=pools)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    if 'loggedin' in session and session['role'] == 'Coach':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if request.method == 'POST':
            description = request.form['description']
            date = request.form['class_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            pool_id = request.form['pool_id']
            lane_no = request.form['lane_no']
            session_type = request.form['session_type']
            price = request.form['price']  # New price field
            coach_id = session['user_id']  # Current coach ID
            
            # Check for conflicts with other lessons
            cursor.execute("""
                SELECT s.session_id 
                FROM session s
                JOIN lesson l ON s.session_id = l.session_id
                WHERE l.coach_id = %s AND s.date = %s
                  AND s.session_id != %s
                  AND (
                      (s.start_time < %s AND s.end_time > %s) OR
                      (s.start_time < %s AND s.end_time > %s) OR
                      (s.start_time >= %s AND s.end_time <= %s)
                  )
            """, (coach_id, date, lesson_id, end_time, start_time, end_time, start_time, start_time, end_time))
            conflict = cursor.fetchone()
            
            if conflict:
                flash('You already have another lesson scheduled during this time.', 'danger')
                return redirect(url_for('edit_lesson', lesson_id=lesson_id))
            
            # Check for conflicts with one-to-one trainings
            cursor.execute("""
                SELECT * FROM session s
                JOIN oneToOneTraining o ON s.session_id = o.session_id
                WHERE o.coach_id = %s AND s.date = %s
                AND s.session_id != %s
                AND (
                    (s.start_time < %s AND s.end_time > %s) OR
                    (s.start_time >= %s AND s.end_time <= %s)
                )
            """, (coach_id, date, lesson_id, end_time, start_time, start_time, end_time))
            training_conflict = cursor.fetchone()

            if training_conflict:
                flash('Conflict detected: You already have a one-to-one training scheduled during this time.', 'danger')
                return redirect(url_for('edit_lesson', lesson_id=lesson_id))

            try:
                # Update session table
                cursor.execute("""
                    UPDATE session
                    SET description = %s, date = %s, start_time = %s, end_time = %s, pool_id = %s, lane_no = %s
                    WHERE session_id = %s
                """, (description, date, start_time, end_time, pool_id, lane_no, lesson_id))
                
                # Update lesson table
                cursor.execute("""
                    UPDATE lesson
                    SET session_type = %s, price = %s
                    WHERE session_id = %s
                """, (session_type, price, lesson_id))
                
                mysql.connection.commit()
                flash('Lesson updated successfully!', 'success')
                return redirect(url_for('homepage'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error updating lesson: {str(e)}', 'danger')
        else:
            # Fetch existing lesson data
            cursor.execute("""
                SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, s.pool_id, s.lane_no, l.capacity, l.session_type, l.price
                FROM session s
                JOIN lesson l ON s.session_id = l.session_id
                WHERE s.session_id = %s
            """, (lesson_id,))
            lesson = cursor.fetchone()
            
            if not lesson:
                flash('Lesson not found!', 'danger')
                return redirect(url_for('homepage'))
            
            # Fetch pools and lanes
            cursor.execute("""
                SELECT pool.pool_id, pool.location, COUNT(lane.lane_no) AS lane_count
                FROM pool
                LEFT JOIN lane ON pool.pool_id = lane.pool_id
                GROUP BY pool.pool_id, pool.location
            """)
            pools = cursor.fetchall()
            
            return render_template('edit_lesson.html', lesson=lesson, pools=pools)
    
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

@app.route('/delete_lesson/<int:lesson_id>', methods=['POST'])
def delete_lesson(lesson_id):
    if 'loggedin' in session and session['role'] == 'Coach':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Delete lesson and its associated session
            cursor.execute('DELETE FROM lesson WHERE session_id = %s', (lesson_id,))
            cursor.execute('DELETE FROM session WHERE session_id = %s', (lesson_id,))
            mysql.connection.commit()
            flash('Lesson deleted successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error deleting lesson: {str(e)}', 'danger')
        return redirect(url_for('homepage'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
@app.route('/create_one_to_one_training', methods=['GET', 'POST'])
def create_one_to_one_training():
    if 'loggedin' in session and session.get('role') == 'Coach':
        if request.method == 'POST':
            description = request.form['description']
            training_date = request.form['training_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            pool_id = request.form['pool_id']
            lane_no = request.form['lane_no']
            swimming_style = request.form['swimming_style']
            price = request.form['price']  # New price field

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Validate Coach Schedule Conflict
            coach_id = session['user_id']
            cursor.execute("""
                SELECT * FROM session s
                JOIN oneToOneTraining o ON s.session_id = o.session_id
                WHERE o.coach_id = %s AND s.date = %s
                  AND (
                      (s.start_time < %s AND s.end_time > %s) OR
                      (s.start_time >= %s AND s.end_time <= %s)
                  )
            """, (coach_id, training_date, end_time, start_time, start_time, end_time))
            conflict = cursor.fetchone()

            if conflict:
                flash('Conflict detected: You already have another session scheduled during this time.', 'danger')
                return redirect(url_for('create_one_to_one_training'))

            # Validate Pool and Lane Conflict
            cursor.execute("""
                SELECT * FROM session 
                WHERE pool_id = %s AND lane_no = %s AND date = %s
                  AND (
                      (start_time < %s AND end_time > %s) OR
                      (start_time >= %s AND end_time <= %s)
                  )
            """, (pool_id, lane_no, training_date, end_time, start_time, start_time, end_time))
            pool_conflict = cursor.fetchone()

            if pool_conflict:
                flash('Conflict detected: Another session overlaps with the selected time and lane.', 'danger')
                return redirect(url_for('create_one_to_one_training'))

            # Check for conflicts with lessons
            cursor.execute("""
                SELECT * FROM session s
                JOIN lesson l ON s.session_id = l.session_id
                WHERE l.coach_id = %s AND s.date = %s
                AND (
                    (s.start_time < %s AND s.end_time > %s) OR
                    (s.start_time >= %s AND s.end_time <= %s)
                )
            """, (coach_id, training_date, end_time, start_time, start_time, end_time))
            lesson_conflict = cursor.fetchone()

            if lesson_conflict:
                flash('Conflict detected: You already have a lesson scheduled during this time.', 'danger')
                return redirect(url_for('create_one_to_one_training'))

            # Insert into session table
            try:
                cursor.execute("""
                    INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (description, pool_id, lane_no, training_date, start_time, end_time))
                mysql.connection.commit()
                session_id = cursor.lastrowid
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error creating session: {str(e)}', 'danger')
                return redirect(url_for('create_one_to_one_training'))

            # Insert into oneToOneTraining table
            try:
                cursor.execute("""
                    INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style, price)
                    VALUES (%s, %s, %s, %s)
                """, (session_id, coach_id, swimming_style, price))
                mysql.connection.commit()
                flash('One-to-One Training created successfully!', 'success')
                return redirect(url_for('homepage'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error creating training: {str(e)}', 'danger')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("""
                SELECT pool.pool_id, pool.location, COUNT(lane.lane_no) AS lane_count
                FROM pool
                LEFT JOIN lane ON pool.pool_id = lane.pool_id
                GROUP BY pool.pool_id, pool.location
            """)
            pools = cursor.fetchall()
            return render_template('create_one_to_one_training.html', pools=pools)
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))

@app.route('/edit_one_to_one_training/<int:training_id>', methods=['GET', 'POST'])
def edit_one_to_one_training(training_id):
    if 'loggedin' in session and session.get('role') == 'Coach':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            description = request.form['description']
            training_date = request.form['training_date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            pool_id = request.form['pool_id']
            lane_no = request.form['lane_no']
            swimming_style = request.form['swimming_style']
            price = request.form['price']  # New price field
            coach_id = session['user_id']

            # Validate Coach Schedule Conflict
            cursor.execute("""
                SELECT * FROM session s
                JOIN oneToOneTraining o ON s.session_id = o.session_id
                WHERE o.coach_id = %s AND s.date = %s
                  AND s.session_id != %s
                  AND (
                      (s.start_time < %s AND s.end_time > %s) OR
                      (s.start_time >= %s AND s.end_time <= %s)
                  )
            """, (coach_id, training_date, training_id, end_time, start_time, start_time, end_time))
            conflict = cursor.fetchone()

            if conflict:
                flash('Conflict detected: You already have another session scheduled during this time.', 'danger')
                return redirect(url_for('edit_one_to_one_training', training_id=training_id))

            # Check for conflicts with lessons
            cursor.execute("""
                SELECT * FROM session s
                JOIN lesson l ON s.session_id = l.session_id
                WHERE l.coach_id = %s AND s.date = %s
                AND s.session_id != %s
                AND (
                    (s.start_time < %s AND s.end_time > %s) OR
                    (s.start_time >= %s AND s.end_time <= %s)
                )
            """, (coach_id, training_date, training_id, end_time, start_time, start_time, end_time))
            lesson_conflict = cursor.fetchone()

            if lesson_conflict:
                flash('Conflict detected: You already have a lesson scheduled during this time.', 'danger')
                return redirect(url_for('edit_one_to_one_training', training_id=training_id))

            try:
                # Update session table
                cursor.execute("""
                    UPDATE session
                    SET description = %s, date = %s, start_time = %s, end_time = %s, pool_id = %s, lane_no = %s
                    WHERE session_id = %s
                """, (description, training_date, start_time, end_time, pool_id, lane_no, training_id))

                # Update oneToOneTraining table
                cursor.execute("""
                    UPDATE oneToOneTraining
                    SET swimming_style = %s, price = %s
                    WHERE session_id = %s
                """, (swimming_style, price, training_id))

                mysql.connection.commit()
                flash('Training updated successfully!', 'success')
                return redirect(url_for('homepage'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error updating training: {str(e)}', 'danger')
        else:
            # Fetch existing training data
            cursor.execute("""
                SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, s.pool_id, s.lane_no, o.swimming_style, o.price
                FROM session s
                JOIN oneToOneTraining o ON s.session_id = o.session_id
                WHERE s.session_id = %s
            """, (training_id,))
            training = cursor.fetchone()

            # Fetch pools and lanes
            cursor.execute("""
                SELECT pool.pool_id, pool.location, COUNT(lane.lane_no) AS lane_count
                FROM pool
                LEFT JOIN lane ON pool.pool_id = lane.pool_id
                GROUP BY pool.pool_id, pool.location
            """)
            pools = cursor.fetchall()
            return render_template('edit_one_to_one_training.html', training=training, pools=pools)
    flash('Unauthorized access!', 'danger')
    return redirect(url_for('login'))


@app.route('/delete_one_to_one_training/<int:training_id>', methods=['POST'])
def delete_one_to_one_training(training_id):
    if 'loggedin' in session and session.get('role') == 'Coach':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('DELETE FROM oneToOneTraining WHERE session_id = %s', (training_id,))
            cursor.execute('DELETE FROM session WHERE session_id = %s', (training_id,))
            mysql.connection.commit()
            flash('Training deleted successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error deleting training: {str(e)}', 'danger')
    return redirect(url_for('homepage'))

#end of coach functions

#################################################################
#### ADMIN FUNCTIONS ############################################
#################################################################

@app.route('/admin_homepage')
def admin_homepage():
    if 'loggedin' in session and session.get('role') == 'Admin':
        forename = session.get('forename', 'Admin')
        # Implement Admin-specific logic and render the admin_homepage.html
        return render_template('admin_homepage.html', forename=forename)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
    
# Admin: Create Coach and Lifeguard Accounts
@app.route('/create_employee', methods=['GET', 'POST'])
def create_employee():
    if 'loggedin' in session and session.get('role') == 'Admin':
        cursor = None
        if request.method == 'POST':
            try:
                # Add validation for required fields
                required_fields = ['role', 'email', 'password', 'forename', 'surname', 'salary', 'emp_date']
                if not all(field in request.form for field in required_fields):
                    flash('All required fields must be filled out!', 'danger')
                    return redirect(url_for('create_employee'))

                role = request.form['role']
                email = request.form['email']
                password = request.form['password']
                forename = request.form['forename']
                surname = request.form['surname']
                salary = request.form['salary']
                emp_date = request.form['emp_date']

                # Validate role-specific required fields
                if role == 'Coach':
                    if not all(field in request.form for field in ['rank', 'specialization']):
                        flash('Rank and specialization are required for Coach!', 'danger')
                        return redirect(url_for('create_employee'))
                elif role == 'Lifeguard':
                    if 'license_no' not in request.form:
                        flash('License number is required for Lifeguard!', 'danger')
                        return redirect(url_for('create_employee'))

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                # Check if email already exists
                cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
                if cursor.fetchone():
                    flash('Email already exists!', 'danger')
                    return redirect(url_for('create_employee'))

                # Insert into user table
                cursor.execute(
                    'INSERT INTO user (email, password, forename, surname, gender, birth_date) '
                    'VALUES (%s, %s, %s, %s, %s, %s)',
                    (email, password, forename, surname, 'Other', '2000-01-01')
                )
                mysql.connection.commit()

                # Get the generated user ID
                cursor.execute('SELECT LAST_INSERT_ID() as user_id')
                user_id = cursor.fetchone()['user_id']

                # Insert into employee table
                cursor.execute(
                    'INSERT INTO employee (user_id, salary, emp_date) VALUES (%s, %s, %s)',
                    (user_id, salary, emp_date)
                )
                mysql.connection.commit()

                # Insert into role-specific table
                if role == 'Coach':
                    rank = request.form['rank']
                    specialization = request.form['specialization']
                    cursor.execute(
                        'INSERT INTO coach (user_id, rank, specialization) VALUES (%s, %s, %s)',
                        (user_id, rank, specialization)
                    )
                elif role == 'Lifeguard':
                    license_no = request.form['license_no']
                    cursor.execute(
                        'INSERT INTO lifeguard (user_id, license_no) VALUES (%s, %s)',
                        (user_id, license_no)
                    )

                mysql.connection.commit()
                flash(f'{role} account created successfully!', 'success')
                return redirect(url_for('admin_homepage'))

            except Exception as e:
                # Handle errors and rollback changes
                if cursor:
                    mysql.connection.rollback()
                print(f"Error details: {str(e)}")  # Add debug print
                flash(f'Error creating {request.form.get("role", "employee")} account: {str(e)}', 'danger')
            finally:
                if cursor:
                    cursor.close()

        return render_template('create_employee.html')
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/generate_report')
def generate_report():
    if 'loggedin' in session and session.get('role') == 'Admin':
        # Generate data for the report
        cursor = mysql.connection.cursor()
        
        # Number of swimmers
        cursor.execute("SELECT COUNT(*) FROM swimmer")
        number_of_swimmer = cursor.fetchone()[0]
        
        # Number of lifeguards
        cursor.execute("SELECT COUNT(*) FROM lifeguard")
        number_of_lifeguard = cursor.fetchone()[0]
        
        # Most liked lesson
        cursor.execute("""
        SELECT l.session_type
        FROM lesson l
        JOIN lessonReview lr ON l.session_id = lr.lesson_id
        JOIN review r ON lr.review_id = r.review_id
        GROUP BY l.session_id
        ORDER BY AVG(r.rating) DESC
        LIMIT 1;
        """)
        most_liked_lesson = cursor.fetchone()
        most_liked_lesson = most_liked_lesson[0] if most_liked_lesson else "No data"

        # Most liked coach
        cursor.execute("""
        SELECT u.forename, u.surname
        FROM user u
        JOIN coachReview cr ON u.user_id = cr.coach_id
        JOIN review r ON cr.review_id = r.review_id
        GROUP BY u.user_id
        ORDER BY AVG(r.rating) DESC
        LIMIT 1
        """)
        most_liked_coach = cursor.fetchone()
        most_liked_coach = f"{most_liked_coach[0]} {most_liked_coach[1]}" if most_liked_coach else "No data"

        # Average queue length
        cursor.execute("SELECT AVG(number_of_waiting) FROM waitQueue")
        average_queue_length = cursor.fetchone()[0]
        average_queue_length = round(average_queue_length, 2) if average_queue_length else 0

        cursor.close()
        
        return render_template(
            'generate_report.html',
            number_of_swimmer=number_of_swimmer,
            number_of_lifeguard=number_of_lifeguard,
            most_liked_lesson=most_liked_lesson,
            most_liked_coach=most_liked_coach,
            average_queue_length=average_queue_length
        )
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

# Admin: View All Bookings
@app.route('/admin_view_bookings')
def admin_view_bookings():
    if 'loggedin' in session and session.get('role') == 'Admin':
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            query = """
                SELECT 
                    b.swimmer_id,
                    b.session_id,
                    b.isCompleted,
                    b.paymentMethod,
                    b.isPaymentCompleted,
                    u.forename,
                    u.surname,
                    s.description,
                    s.date,
                    s.start_time,
                    s.end_time
                FROM booking b
                JOIN user u ON b.swimmer_id = u.user_id
                JOIN session s ON b.session_id = s.session_id
                ORDER BY s.date, s.start_time
            """
            cursor.execute(query)
            bookings = cursor.fetchall()
            print("Fetched bookings:", bookings)  # Debug print
            
            cursor.close()
            return render_template('admin_view_bookings.html', bookings=bookings)
        except Exception as e:
            print("Database error:", str(e))  # Debug print
            flash(f'Error fetching bookings: {str(e)}', 'danger')
            return redirect(url_for('admin_homepage'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

# Admin: View All Users
@app.route('/admin_view_users')
def admin_view_users():
    if 'loggedin' in session and session.get('role') == 'Admin':
        cursor = mysql.connection.cursor()
        try:
            # SQL Query to fetch users and their roles
            query = """
            SELECT 
                u.user_id,
                SUBSTRING_INDEX(u.forename, '-', 1) AS forename,
                u.surname,
                CASE 
                    WHEN c.user_id IS NOT NULL THEN 'Coach'
                    WHEN l.user_id IS NOT NULL THEN 'Lifeguard'
                    WHEN a.user_id IS NOT NULL THEN 'Admin'
                    ELSE 'Swimmer'
                END AS role
            FROM user u
            LEFT JOIN coach c ON u.user_id = c.user_id
            LEFT JOIN lifeguard l ON u.user_id = l.user_id
            LEFT JOIN pool_admin a ON u.user_id = a.user_id;
            """
            cursor.execute(query)
            users = cursor.fetchall()

            # Debug output to verify fetched data
            print("Fetched Users:", users)

        except Exception as e:
            print("Error fetching users:", str(e))
            flash("Error fetching user data.", "danger")
            users = []
        finally:
            cursor.close()

        # Render the template with fetched users
        return render_template('admin_view_users.html', users=users)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/update_payment_status/<int:swimmer_id>/<int:session_id>', methods=['POST'])
def update_payment_status(swimmer_id, session_id):
    if 'loggedin' in session and session.get('role') == 'Admin':
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE booking 
                SET isPaymentCompleted = TRUE 
                WHERE swimmer_id = %s AND session_id = %s
            """, (swimmer_id, session_id))
            mysql.connection.commit()
            cursor.close()
            flash('Payment status updated successfully!', 'success')
        except Exception as e:
            flash('Error updating payment status!', 'danger')
        return redirect(url_for('admin_view_bookings'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
