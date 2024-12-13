from flask import Flask, render_template, request, redirect, url_for, session
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

@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('tasks'))
        else:
            message = 'Invalid username or password!'
    return render_template('login.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            message = 'Username already exists!'
        else:
            cursor.execute('INSERT INTO User (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            message = 'Registration successful!'
            return redirect(url_for('login'))
    return render_template('register.html', message=message)


@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:  # Check if the user is logged in
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))



@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if 'loggedin' in session:  # Check if the user is logged in
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if request.method == 'POST' and 'course_id' in request.form:
            course_id = request.form['course_id']
            cursor.execute(
                'SELECT * FROM Registration WHERE user_id = %s AND course_id = %s',
                (session['userid'], course_id)
            )
            registration = cursor.fetchone()
            if registration:
                message = 'You are already registered for this course!'
            else:
                cursor.execute(
                    'INSERT INTO Registration (user_id, course_id) VALUES (%s, %s)',
                    (session['userid'], course_id)
                )
                mysql.connection.commit()
                message = 'Course registered successfully!'
        else:
            message = ''
        
        # Fetch all courses
        cursor.execute('SELECT * FROM Course')
        courses = cursor.fetchall()
        return render_template('courses.html', courses=courses, message=message)
    
    return redirect(url_for('login'))
