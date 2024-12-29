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
        return render_template('swimmer_homepage.html', forename=forename)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
@app.route('/swimmer_lessons')
def lessons():
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        forename = session.get('forename', 'Member')
        swimmer_id = session['user_id']

        class_date = request.args.get('class_date')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        pool_id = request.args.get('pool_id')
        session_type = request.args.get('session_type')
        coach_id = request.args.get('coach_id')
        min_capacity = request.args.get('min_capacity')
        max_capacity = request.args.get('max_capacity')

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
            return redirect(url_for('lessons'))
        
        # Check if the lesson is full
        cursor.execute('SELECT capacity, student_count, session_type FROM lesson WHERE session_id = %s', (session_id,))
        lesson = cursor.fetchone()

        lesson_type = lesson['session_type']
        if (lesson_type == 'FemaleOnly' and user_gender != 'Female') or (lesson_type == 'MaleOnly' and user_gender != 'Male'):
            flash(f'This lesson is restricted to {lesson_type}. Your gender: {user_gender} does not match the requirement.', 'warning')
            return redirect(url_for('lessons'))
        
        if lesson['student_count'] >= lesson['capacity']:
            flash('Cannot enroll: The lesson is full.', 'danger')
            return redirect(url_for('lessons'))
        
        # Enroll the swimmer
        try:
            cursor.execute('INSERT INTO booking (swimmer_id, session_id) VALUES (%s, %s)', (swimmer_id, session_id))
            mysql.connection.commit()
            flash('Successfully enrolled in the lesson!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error enrolling in lesson: {str(e)}', 'danger')
        
        return redirect(url_for('lessons'))
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
            return redirect(url_for('lessons'))
        
        # Exit the lesson
        try:
            cursor.execute('DELETE FROM booking WHERE swimmer_id = %s AND session_id = %s', (swimmer_id, session_id))
            mysql.connection.commit()
            flash('Successfully exited the lesson.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error exiting lesson: {str(e)}', 'danger')
        
        return redirect(url_for('lessons'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/swimmer_free_session')
def free_session():
    if 'loggedin' in session and (session.get('role') == 'Member' or session.get('role') == 'Swimmer'):
        forename = session.get('forename', 'Member')
        return render_template('swimmer_free_session.html', forename=forename)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/swimmer_one_to_one_training')
def one_to_one_training():
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
                   s.pool_id, s.lane_no, l.session_type
            FROM lesson l
            JOIN session s ON l.session_id = s.session_id
            WHERE l.coach_id = %s
        """, (coach_id,))
        lessons = cursor.fetchall()

        # Fetch One-to-One Trainings
        cursor.execute("""
            SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, 
                   s.pool_id, s.lane_no, o.swimming_style
            FROM oneToOneTraining o
            JOIN session s ON o.session_id = s.session_id
            WHERE o.coach_id = %s
        """, (coach_id,))
        one_to_one_trainings = cursor.fetchall()

        return render_template(
            'coach_homepage.html',
            forename=forename,
            lessons=lessons,
            one_to_one_trainings=one_to_one_trainings
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
            session_type = request.form['session_type']  # New field
            
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
            
            # Insert into session table
            try:
                cursor.execute('INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)',
                               (description, pool_id, lane_no, class_date, start_time, end_time))
                mysql.connection.commit()
                session_id = cursor.lastrowid  # Get the generated session_id
            except Exception as e:
                mysql.connection.rollback()
                flash('Error creating session: {}'.format(str(e)), 'danger')
                return redirect(url_for('create_lesson'))
            
            # Insert into lesson table
            try:
                coach_id = session['user_id']
                cursor.execute('INSERT INTO lesson (session_id, coach_id, student_count, capacity, session_type) VALUES (%s, %s, %s, %s, %s)',
                               (session_id, coach_id, 0, capacity, session_type))
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

            return render_template('create_one_.html', pools=pools)
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
            
            try:
                cursor.execute("""
                    UPDATE session
                    SET description = %s, date = %s, start_time = %s, end_time = %s, pool_id = %s, lane_no = %s
                    WHERE session_id = %s
                """, (description, date, start_time, end_time, pool_id, lane_no, lesson_id))
                cursor.execute("""
                    UPDATE lesson
                    SET session_type = %s
                    WHERE session_id = %s
                """, (session_type, lesson_id))
                mysql.connection.commit()
                flash('Lesson updated successfully!', 'success')
                return redirect(url_for('homepage'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error updating lesson: {str(e)}', 'danger')
        else:
            cursor.execute("""
                SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, s.pool_id, s.lane_no, l.capacity, l.session_type
                FROM session s
                JOIN lesson l ON s.session_id = l.session_id
                WHERE s.session_id = %s
            """, (lesson_id,))
            lesson = cursor.fetchone()
            
            if not lesson:
                flash('Lesson not found!', 'danger')
                return redirect(url_for('homepage'))
            
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
            """, (pool_id, lane_no, training_date, end_time, start_time, end_time, start_time, start_time, end_time))
            conflict = cursor.fetchone()

            if conflict:
                flash('Conflict detected: Another session overlaps with the selected time and lane.', 'danger')
                return redirect(url_for('create_one_to_one_training'))
            
            try:
                cursor.execute('INSERT INTO session (description, pool_id, lane_no, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)',
                               (description, pool_id, lane_no, training_date, start_time, end_time))
                mysql.connection.commit()
                session_id = cursor.lastrowid
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error creating session: {str(e)}', 'danger')
                return redirect(url_for('create_one_to_one_training'))
            
            try:
                coach_id = session['user_id']
                cursor.execute('INSERT INTO oneToOneTraining (session_id, coach_id, swimming_style) VALUES (%s, %s, %s)',
                               (session_id, coach_id, swimming_style))
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
            
            try:
                cursor.execute("""
                    UPDATE session
                    SET description = %s, date = %s, start_time = %s, end_time = %s, pool_id = %s, lane_no = %s
                    WHERE session_id = %s
                """, (description, training_date, start_time, end_time, pool_id, lane_no, training_id))
                cursor.execute("""
                    UPDATE oneToOneTraining
                    SET swimming_style = %s
                    WHERE session_id = %s
                """, (swimming_style, training_id))
                mysql.connection.commit()
                flash('Training updated successfully!', 'success')
                return redirect(url_for('homepage'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error updating training: {str(e)}', 'danger')
        else:
            cursor.execute("""
                SELECT s.session_id, s.description, s.date, s.start_time, s.end_time, s.pool_id, s.lane_no, o.swimming_style
                FROM session s
                JOIN oneToOneTraining o ON s.session_id = o.session_id
                WHERE s.session_id = %s
            """, (training_id,))
            training = cursor.fetchone()
            
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
#end of admin functions    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
