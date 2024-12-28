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
    return 'User'


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
        password = request.form['password']  # Plain text password
        
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
        role = session.get('role', 'User')
        forename = session.get('forename', 'User')
        
        if role == 'Admin':
            return render_template('admin_homepage.html', forename=forename)
        elif role == 'Coach':
            return render_template('coach_homepage.html', forename=forename)
        elif role == 'Lifeguard':
            return render_template('lifeguard_homepage.html', forename=forename)
        elif role == 'Member':
            return render_template('member_homepage.html', forename=forename)
        else:
            return render_template('homepage.html', forename=forename)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
