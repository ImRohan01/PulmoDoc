from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask import send_from_directory
import MySQLdb.cursors
import os
import re
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from keras.models import load_model
import cv2
import model

global graph
graph = tf.get_default_graph()
init_op = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init_op)

Model = load_model('static/PneumoniaModel.h5')
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.secret_key = 'databaseiscool'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'laxmi1234'
app.config['MYSQL_DB'] = 'pulmodoc'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            session['fullname'] = account['fullname']
            session['email'] = account['email']
            session['role'] = role
            print(account)

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password/role!'
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
    if 'loggedin' in session and session['role']=='Admin':
        # User is loggedin show them the home page
        return redirect(url_for('viewfeedback'))
    if 'loggedin' in session and session['role']=='Doctor':
        # User is loggedin show them the home page
        return render_template('dochome.html', fullname=session['fullname'])
    if 'loggedin' in session and session['role']=='Patient':
        # User is loggedin show them the home page
        return render_template('pathome.html', fullname=session['fullname'])
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
        account['role'] = session['role']
        if session['role'] =="Doctor":
            return render_template('doctor_profile.html', account=account)
        if session['role'] =="Patient":
            return render_template('patprofile.html', account=account)
        if session['role'] =="Admin":
            return render_template('adminprofile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pulmodoc/editdocprofile/', methods=['GET','POST'])
def editdocprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and ('fullname' in request.form or 'password' in request.form or 'email' in request.form or 'phone' in request.form or 'degree' in request.form or 'image' in request.form):
        id = session['id']
        if request.form['fullname']:
            fullname = request.form['fullname']
            cursor.execute("UPDATE doctor_register SET fullname = %s WHERE id = %s",[fullname,id])
        if request.form['email']:
            email = request.form['email']
            cursor.execute("UPDATE doctor_register SET email = %s WHERE id = %s",[email,id])
        if request.form['password']:
            password = request.form['password']
            cursor.execute("UPDATE doctor_register SET password = %s WHERE id = %s",[password,id])
        if request.form['phone']:
            phone = request.form['phone']
            cursor.execute("UPDATE doctor_register SET phone = %s WHERE id = %s",[phone,id])
        if request.form['degree']:
            degree = request.form['degree']
            cursor.execute("UPDATE doctor_register SET degree = %s WHERE id = %s",[degree,id])
        if request.files['image']:
            file = request.files['image']
            image = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(image)
            filename = secure_filename(file.filename)
            cursor.execute("UPDATE doctor_register SET image = %s WHERE id = %s",[filename,id])
        #if 'image' in request.form:
        #cursor.execute("UPDATE doctor_register SET image = %s WHERE id = %s",[image,id])
    mysql.connection.commit()
    return redirect(url_for('profile'))

@app.route('/pulmodoc/editpatprofile/', methods=['GET','POST'])
def editpatprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and ('fullname' in request.form or 'password' in request.form or 'email' in request.form or 'phone' in request.form):
        id = session['id']
        if request.form['fullname']:
            fullname = request.form['fullname']
            cursor.execute("UPDATE patient_register SET fullname = %s WHERE id = %s",[fullname,id])
        if request.form['email']:
            email = request.form['email']
            cursor.execute("UPDATE patient_register SET email = %s WHERE id = %s",[email,id])
        if request.form['password']:
            password = request.form['password']
            cursor.execute("UPDATE patient_register SET password = %s WHERE id = %s",[password,id])
        if request.form['phone']:
            phone = request.form['phone']
            cursor.execute("UPDATE patient_register SET phone = %s WHERE id = %s",[phone,id])
    mysql.connection.commit()
    return redirect(url_for('profile'))

@app.route('/pulmodoc/editadminprofile/', methods=['GET','POST'])
def editadminprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST' and ('fullname' in request.form or 'password' in request.form or 'email' in request.form or 'phone' in request.form):
        id = session['id']
        if request.form['fullname']:
            fullname = request.form['fullname']
            cursor.execute("UPDATE admin_register SET fullname = %s WHERE id = %s",[fullname,id])
        if request.form['email']:
            email = request.form['email']
            cursor.execute("UPDATE admin_register SET email = %s WHERE id = %s",[email,id])
        if request.form['password']:
            password = request.form['password']
            cursor.execute("UPDATE admin_register SET password = %s WHERE id = %s",[password,id])
        if request.form['phone']:
            phone = request.form['phone']
            cursor.execute("UPDATE admin_register SET phone = %s WHERE id = %s",[phone,id])
    mysql.connection.commit()
    return redirect(url_for('profile'))

@app.route('/pulmodoc/changedocprofile/')
def changedocprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM doctor_register WHERE id = %s', [session['id']])
    account = cursor.fetchone()
    mysql.connection.commit()
    return render_template('editdocprofile.html', account=account)

@app.route('/pulmodoc/changepatprofile/')
def changepatprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM patient_register WHERE id = %s', [session['id']])
    account = cursor.fetchone()
    mysql.connection.commit()
    return render_template('editpatprofile.html', account=account)

@app.route('/pulmodoc/changeadminprofile/')
def changeadminprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM admin_register WHERE id = %s', [session['id']])
    account = cursor.fetchone()
    mysql.connection.commit()
    return render_template('editadminprofile.html',account=account)

@app.route('/pulmodoc/totestresults/')
def totestresults():
    return render_template('testxray.html')

@app.route('/pulmodoc/tofeedback/')
def tofeedback():
    return render_template('feedback.html')

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/pulmodoc/testimages/', methods=['POST','GET'])
def testxray():
    patid = ""
    diagnosis = ""
    flag = 0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        id = session['id']
        patname = request.form['patname']
        patmail = request.form['patmail']
        utn = request.form['utn']
        cursor.execute("SELECT * FROM test_results WHERE utn = %s",[utn])
        account = cursor.fetchone()
        if account:
            msg = "Test number is not unique"
            mysql.connection.commit()
            return render_template("testxray.html",msg=msg)
        cursor.execute("SELECT id from patient_register WHERE email = %s",[patmail])
        patid = cursor.fetchone()
        patid = patid['id']
        result = ""
        #
        file = request.files['image']
        image = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image)
        filename = secure_filename(file.filename)
        img = cv2.imread(image)
        img = cv2.resize(img, (224,224))
        img = img.reshape(1,224,224,3)
        with graph.as_default():
            result = model.predict(filename)
        print(result)
        cursor.execute("INSERT INTO test_results VALUES(%s,%s,%s,%s,%s)",[utn,filename,result,id,patid])
        cursor.execute('SELECT fullname,email FROM patient_register WHERE id = %s',[patid])
        patient = cursor.fetchone()
        cursor.execute('SELECT * FROM test_results WHERE utn = %s',[utn])
        account = cursor.fetchone()
        mysql.connection.commit()
        return render_template("testresults.html",account=account,patient=patient,diagnosis=diagnosis,flag=flag)
    mysql.connection.commit()
    return redirect(url_for('home'))

@app.route('/pulmodoc/feedback/', methods=['POST','GET'])
def feedback():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    msg = ""
    if request.method == 'POST':
        if session['role']=='Doctor':
            id = session['id']
            text = request.form['feedback']
            utn = request.form['utn']
            cursor.execute('SELECT * FROM test_results WHERE utn = %s',[utn])
            account = cursor.fetchone()
            if not account:
                msg="The UTN does not exist!"
                mysql.connection.commit()
                return render_template("feedback.html",msg=msg)
            cursor.execute("INSERT INTO feedback VALUES(NULL,%s,%s,%s,NULL)",[utn,text,id])
        if session['role']=='Patient':
            id = session['id']
            text = request.form['feedback']
            utn = request.form['utn']
            cursor.execute('SELECT * FROM test_results WHERE utn = %s',[utn])
            account = cursor.fetchone()
            if not account:
                msg="The UTN does not exist!"
                mysql.connection.commit()
                return render_template("feedback.html",msg=msg)
            cursor.execute("INSERT INTO feedback VALUES(NULL,%s,%s,NULL,%s)",[utn,text,id])
        msg = "Feedback has been sent successfully!"
    mysql.connection.commit()
    return render_template("feedback.html",msg=msg)

@app.route('/pulmodoc/viewfeedback/', methods=['GET'])
def viewfeedback():
    name1 = {}
    name2 = {}
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM feedback WHERE docid > 0")
    account1 = cursor.fetchall()
    print(account1)
    for account in account1:
        print(account)
        cursor.execute("SELECT fullname FROM doctor_register WHERE id = %s",[account['docid']])
        temp = cursor.fetchone()
        name1[account['fbackid']] = temp['fullname']

    cursor.execute("SELECT * FROM feedback WHERE patid > 0")
    account2 = cursor.fetchall()
    for account in account2:
        cursor.execute("SELECT fullname FROM patient_register WHERE id = %s",[account['patid']])
        temp = cursor.fetchone()
        name2[account['fbackid']] = temp['fullname']

    mysql.connection.commit()
    return render_template("viewfeedback.html", account1=account1,name1=name1,name2=name2,account2=account2,fullname=session['fullname'])

@app.route('/pulmodoc/dispfeedback/', methods=['GET','POST'])
def dispfeedback():
    id = request.form['fbackid']
    name = request.form['name']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM feedback WHERE fbackid=%s",[id])
    account = cursor.fetchone()
    mysql.connection.commit()
    return render_template("dispfeedback.html",account = account, name = name)

@app.route('/pulmodoc/testdetails/', methods=['GET','POST'])
def testdetails():
    names = {}
    docid = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM test_results WHERE docid = %s",[docid])
    accounts = cursor.fetchall()
    for account in accounts:
        patid = account['patid']
        cursor.execute("SELECT fullname FROM patient_register WHERE id = %s", [patid])
        names[patid] = cursor.fetchone()['fullname']
    mysql.connection.commit()
    return render_template("testdetails.html", accounts=accounts, names=names)

@app.route('/pulmodoc/disptestdetails/',methods=['GET','POST'])
def disptestdetails():
    utn = request.form['utn']
    flag = 1
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM test_results WHERE utn = %s",[utn])
    account = cursor.fetchone()
    patid = account['patid']
    cursor.execute('SELECT fullname,email FROM patient_register WHERE id = %s',[patid])
    patient = cursor.fetchone()
    cursor.execute("SELECT * FROM diagnosis WHERE utn = %s",[utn])
    diagnosis = cursor.fetchone()
    mysql.connection.commit()
    return render_template('testresults.html',account=account,patient=patient,diagnosis=diagnosis,flag=flag)

@app.route('/pulmodoc/updatediagnosis', methods=['GET','POST'])
def updatediagnosis():
    diagnosis = request.form['diagnosis']
    utn = request.form['utn']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO diagnosis VALUES(NULL,%s,%s)",[utn,diagnosis])
    mysql.connection.commit()
    return redirect(url_for('testdetails'))

@app.route('/pulmodoc/patienttestdetails/', methods=['GET','POST'])
def patienttestdetails():
    names = {}
    patid = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM test_results WHERE patid = %s",[patid])
    accounts = cursor.fetchall()
    for account in accounts:
        docid = account['docid']
        cursor.execute("SELECT fullname FROM doctor_register WHERE id = %s", [docid])
        names[docid] = cursor.fetchone()['fullname']
    mysql.connection.commit()
    return render_template("pattestdetails.html", accounts=accounts, names=names)

@app.route('/pulmodoc/disppattestdetails/',methods=['GET','POST'])
def disppattestdetails():
    utn = request.form['utn']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM test_results WHERE utn = %s",[utn])
    account = cursor.fetchone()
    patid = account['patid']
    cursor.execute('SELECT fullname,email FROM patient_register WHERE id = %s',[patid])
    patient = cursor.fetchone()
    cursor.execute("SELECT * FROM diagnosis WHERE utn = %s",[utn])
    diagnosis = cursor.fetchone()
    mysql.connection.commit()
    return render_template('pattestresults.html',account=account,patient=patient,diagnosis=diagnosis)
