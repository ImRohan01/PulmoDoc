from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'databaseiscool'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'laxmi1234'
app.config['MYSQL_DB'] = 'pulmodoc'

mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pulmodoc/', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        role     = request.form.get('role')
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if role=="Doctor":
            cursor.execute('SELECT * FROM doctor_register WHERE email = %s AND password = %s', [email, password])
        elif role=="Patient":
            cursor.execute('SELECT * FROM patient_register WHERE email = %s AND password = %s', [email, password])
        else:
            cursor.execute('SELECT * FROM admin_register WHERE email = %s AND password = %s', [email, password])

        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['role'] = role
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
    # Show login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pulmodoc/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pulmodoc/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'fullname' in request.form and 'password' in request.form and 'email' in request.form and 'phone' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form.get('role')

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if role=="Doctor":
            cursor.execute('SELECT * FROM doctor_register WHERE email = %s', [email])
        elif role=="Patient":
            cursor.execute('SELECT * FROM patient_register WHERE email = %s', [email])
        else:
            cursor.execute('SELECT * FROM admin_register WHERE email = %s', [email])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Z a-z]+', fullname):
            msg = 'Fullname must contain only alphabets and space!'
        elif not re.match(r'[0-9]+', phone):
            phone = 'Phone must contain only numbers!'
        elif not fullname or not password or not email or not phone:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            if role == "Doctor":
                cursor.execute('INSERT INTO doctor_register VALUES (NULL, %s, %s, %s, NULL, NULL, %s)', [fullname, email, password, phone])
            elif role=="Patient":
                cursor.execute('INSERT INTO patient_register VALUES (NULL, %s, %s, %s, %s)', [fullname, email, password, phone])
            else:
                cursor.execute('INSERT INTO admin_register VALUES (NULL, %s, %s, %s, %s)', [fullname, email, password, phone])
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pulmodoc/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', email=session['email'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pulmodoc/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if session['role']=="Doctor":
            cursor.execute('SELECT * FROM doctor_register WHERE id = %s', [session['id']])
        if session['role']=="Patient":
            cursor.execute('SELECT * FROM patient_register WHERE id = %s', [session['id']])
        if session['role']=="Admin":
            cursor.execute('SELECT * FROM admin_register WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
