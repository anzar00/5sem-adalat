from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, string, random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
app.secret_key = '23092000'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'DBAdmin@123$'
app.config['MYSQL_DB'] = 'adalat'

mysql = MySQL(app)

#Home Page
@app.route("/")
@app.route("/home")
def home_page():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) FROM `Case`')
        count = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM Lawyer')
        l_count = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM Judge')
        j_count = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM `Case` WHERE status = 'Pending'")
        p_count = cursor.fetchone()
        cursor.execute('SELECT * FROM Lawyer')
        lawyer = cursor.fetchall()    
        return render_template('./admin/index.html',  username=session['username'],count=count,l_count=l_count,j_count=j_count,p_count=p_count,lawyer = lawyer)
    return render_template('home.html')

#### Login Routes ####

#Admin Login
@app.route("/home", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM MasterLogin WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT COUNT(*) FROM `Case`')
            count = cursor.fetchone()
            cursor.execute('SELECT COUNT(*) FROM Lawyer')
            l_count = cursor.fetchone()
            cursor.execute('SELECT COUNT(*) FROM Judge')
            j_count = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM `Case` WHERE status = 'Pending'")
            p_count = cursor.fetchone()
            cursor.execute('SELECT * FROM Lawyer')
            lawyer = cursor.fetchall()    
            return render_template('./admin/index.html',  username=session['username'],count=count,l_count=l_count,j_count=j_count,p_count=p_count,lawyer = lawyer)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('home.html', msg = msg)


#Citizen Login
@app.route("/citizen/home")
def citizen_login_page():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) FROM `Case`')
        count = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM Lawyer')
        count_l = cursor.fetchone()   
        cursor.execute('SELECT COUNT(*) FROM Judge')
        count_j = cursor.fetchone()   
        cursor.execute('SELECT COUNT(*) FROM Citizen')
        count_c = cursor.fetchone()  
        return render_template('./citizen/index.html', uname=session['name'],count=count,count_l=count_l,count_j=count_j,count_c=count_c)
    return render_template('home.html')
@app.route("/login/citizen", methods=['GET', 'POST'])
def citizen_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Citizen WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['ClientId']
            session['email'] = account['email']
            session['name'] = account['Name']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT COUNT(*) FROM `Case`')
            count = cursor.fetchone()  
            cursor.execute('SELECT COUNT(*) FROM Lawyer')
            count_l = cursor.fetchone()  
            cursor.execute('SELECT COUNT(*) FROM Judge')
            count_j = cursor.fetchone()   
            cursor.execute('SELECT COUNT(*) FROM Citizen')
            count_c = cursor.fetchone()   
            # Redirect to home page
            return render_template('./citizen/index.html', uname=session['name'],count=count,count_l=count_l,count_j=count_j,count_c=count_c)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('home.html', msg = msg)

#Lawyer Login
@app.route("/login/lawyer")
def lawyer_login_page():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        email = session['email']
        cursor.execute('SELECT COUNT(*) FROM `Case`')
        count = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s)',(email,))
        count_l = cursor.fetchone()   
        cursor.execute('SELECT COUNT(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s) AND status = "Pending"',(email,))
        count_a = cursor.fetchone()   
        cursor.execute('SELECT COUNT(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s) AND status = "Closed"',(email,))
        count_c = cursor.fetchone() 
        return render_template('./lawyer/index.html', name=session['name'],count=count,count_l=count_l,count_a=count_a,count_c=count_c)
    return render_template('lawyer-login.html')
@app.route("/login/lawyer", methods=['GET', 'POST'])
def lawyer_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Lawyer WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['LawyerId']
            session['email'] = account['email']
            session['name'] = account['Name']
            # Redirect to home page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            email = session['email']
            cursor.execute('SELECT COUNT(*) FROM `Case`')
            count = cursor.fetchone()
            cursor.execute('SELECT COUNT(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s)',(email,))
            count_l = cursor.fetchone()   
            cursor.execute('SELECT COUNT(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s) AND status = "Pending"',(email,))
            count_a = cursor.fetchone()   
            cursor.execute('SELECT COUNT(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s) AND status = "Closed"',(email,))
            count_c = cursor.fetchone() 
            return render_template('./lawyer/index.html', name=session['name'],count=count,count_l=count_l,count_a=count_a,count_c=count_c)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
    # Show the login form with message (if any)
    return render_template('lawyer-login.html', msg = msg)


#Judge Login
@app.route("/login/judge")
def judge_login_page():
    if 'loggedin' in session:
        return render_template('./judge/index.html', name=session['name'])
    return render_template('judge-login.html')
@app.route("/login/judge", methods=['GET', 'POST'])
def judge_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Judge WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['JudgeId']
            session['email'] = account['email']
            session['name'] = account['Name']
            # Redirect to home page
            return render_template('./judge/index.html', name=session['name'])
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password!'
    # Show the login form with message (if any)
    return render_template('judge-login.html', msg = msg)


#### Login Routes End ####


#Logout API
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

#About Page
@app.route("/about")
def about_page():
    return render_template('about.html')



#### Registration Routes ####

#Admin Registration
@app.route("/register",)
def register_page():
    return render_template('register.html')
@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM MasterLogin WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO MasterLogin VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

#Citizen Registration
@app.route("/register/citizen")
def register_citizen_page():
    return render_template('register-citizen.html')
@app.route("/register/citizen", methods=['GET', 'POST'])
def register_citizen():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'address' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']

        #Random Password Generation
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

        def generate_random_password():

            length = 8
            random.shuffle(characters)
            password = []
                
            for i in range(length):
                password.append(random.choice(characters))
                
            random.shuffle(password)

            return ("".join(password))

        #Password Generation End

        pass_word = generate_random_password()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Citizen WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not contact or not address:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO Citizen (Name,email,contact,address,password) VALUES (%s, %s, %s, %s, %s)', (name, email, contact, address, pass_word,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

            # Sending Mail
            

            sender_email = "adalat.app@gmail.com"
            receiver_email = email
            password = 'Adalat@123$'

            message = MIMEMultipart("alternative")
            message["Subject"] = ("Dear "+ name +" , Please Note Your Credentials For Adalat")
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            Hi, """+name+"""
            Please note your credentials for Adalat<br>
            Your Email is - """+email+""", and
            Password is - ""+pass_word+
            """
            html = """\
            <html>
            <body>
                <p>Hi,"""+name+"""<br>
                Please note your credentials for Adalat<br>
                Your <b>Email</b> is - """+email+""", and<br>
                <b>Password</b> is - """+pass_word+"""
                </p>
            </body>
            </html>
            """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            # End Mail 
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register-citizen.html', msg=msg)

#Lawyer Registration
@app.route("/register/lawyer")
def register_lawyer_page():
    return render_template('register-lawyer.html')
@app.route("/register/lawyer", methods=['GET', 'POST'])
def register_lawyer():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'address' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']

        #Random Password Generation
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

        def generate_random_password():

            length = 8
            random.shuffle(characters)
            password = []
                
            for i in range(length):
                password.append(random.choice(characters))
                
            random.shuffle(password)

            return ("".join(password))

        #Password Generation End

        pass_word = generate_random_password()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Lawyer WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not contact or not address:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO Lawyer (Name,email,contact,address,password) VALUES (%s, %s, %s, %s, %s)', (name, email, contact, address, pass_word,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

            # Sending Mail
            

            sender_email = "adalat.app@gmail.com"
            receiver_email = email
            password = 'Adalat@123$'

            message = MIMEMultipart("alternative")
            message["Subject"] = ("Dear "+ name +" , Please Note Your Credentials For Adalat")
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            Hi, """+name+"""
            Please note your credentials for Adalat<br>
            Your Email is - """+email+""", and
            Password is - ""+pass_word+
            """
            html = """\
            <html>
            <body>
                <p>Hi,"""+name+"""<br>
                Please note your credentials for Adalat<br>
                Your <b>Email</b> is - """+email+""", and<br>
                <b>Password</b> is - """+pass_word+"""
                </p>
            </body>
            </html>
            """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            # End Mail 
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register-lawyer.html', msg=msg)

#Judge Registration
@app.route("/register/judge")
def register_judge_page():
    return render_template('register-judge.html')
@app.route("/register/judge", methods=['GET', 'POST'])
def register_judge():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'address' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']

        #Random Password Generation
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

        def generate_random_password():

            length = 8
            random.shuffle(characters)
            password = []
                
            for i in range(length):
                password.append(random.choice(characters))
                
            random.shuffle(password)

            return ("".join(password))

        #Password Generation End

        pass_word = generate_random_password()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Judge WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not contact or not address:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO Judge (Name,email,contact,address,password) VALUES (%s, %s, %s, %s, %s)', (name, email, contact, address, pass_word,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

            # Sending Mail
            

            sender_email = "adalat.app@gmail.com"
            receiver_email = email
            password = 'Adalat@123$'

            message = MIMEMultipart("alternative")
            message["Subject"] = ("Dear "+ name +" , Please Note Your Credentials For Adalat")
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            Hi, """+name+"""
            Please note your credentials for Adalat<br>
            Your Email is - """+email+""", and
            Password is - ""+pass_word+
            """
            html = """\
            <html>
            <body>
                <p>Hi,"""+name+"""<br>
                Please note your credentials for Adalat<br>
                Your <b>Email</b> is - """+email+""", and<br>
                <b>Password</b> is - """+pass_word+"""
                </p>
            </body>
            </html>
            """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            # End Mail 
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register-judge.html', msg=msg)

#### Registration Routes End####


### Admin Routes ###

@app.route("/admin/add-lawyer")
def add_lawyer_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Lawyer')
    lawyer = cursor.fetchall() 
    return render_template('./admin/add-lawyer.html',username=session['username'],lawyer=lawyer)

@app.route("/admin/add-lawyer", methods=['GET', 'POST'])
def add_lawyer():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'address' in request.form and 'contact' in request.form and 'email' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']

        #Random Password Generation
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

        def generate_random_password():

            length = 8
            random.shuffle(characters)
            password = []
                
            for i in range(length):
                password.append(random.choice(characters))
                
            random.shuffle(password)

            return ("".join(password))

        #Password Generation End

        pass_word = generate_random_password()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Lawyer WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not contact or not address:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO Lawyer (Name,email,contact,address,password) VALUES (%s, %s, %s, %s, %s)', (name, email, contact, address, pass_word,))
            mysql.connection.commit()
            msg = 'Lawyer Added!'

            # Sending Mail
            

            sender_email = "adalat.app@gmail.com"
            receiver_email = email
            password = 'Adalat@123$'

            message = MIMEMultipart("alternative")
            message["Subject"] = ("Dear "+ name +" , Please Note Your Credentials For Adalat")
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            Hi, """+name+"""
            Please note your credentials for Adalat<br>
            Your Email is - """+email+""", and
            Password is - ""+pass_word+
            """
            html = """\
            <html>
            <body>
                <p>Hi,"""+name+"""<br>
                Please note your credentials for Adalat<br>
                Your <b>Email</b> is - """+email+""", and<br>
                <b>Password</b> is - """+pass_word+"""
                </p>
            </body>
            </html>
            """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            # End Mail 
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Lawyer')
    lawyer = cursor.fetchall()  
    return render_template('./admin/add-lawyer.html', msg=msg, username=session['username'], lawyer=lawyer)


@app.route("/admin/add-judge")
def add_judge_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Judge')
    judge = cursor.fetchall() 
    return render_template('./admin/add-judge.html',username=session['username'],judge=judge)

@app.route("/admin/add-judge", methods=['GET', 'POST'])
def add_judge():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'contact' in request.form and 'address' in request.form:
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']

        #Random Password Generation
        characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

        def generate_random_password():

            length = 8
            random.shuffle(characters)
            password = []
                
            for i in range(length):
                password.append(random.choice(characters))
                
            random.shuffle(password)

            return ("".join(password))

        #Password Generation End

        pass_word = generate_random_password()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Judge WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not name or not contact or not address:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO Judge (Name,email,contact,address,password) VALUES (%s, %s, %s, %s, %s)', (name, email, contact, address, pass_word,))
            mysql.connection.commit()
            msg = 'Judge Added!'

            # Sending Mail
            

            sender_email = "adalat.app@gmail.com"
            receiver_email = email
            password = 'Adalat@123$'

            message = MIMEMultipart("alternative")
            message["Subject"] = ("Dear "+ name +" , Please Note Your Credentials For Adalat")
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            Hi, """+name+"""
            Please note your credentials for Adalat<br>
            Your Email is - """+email+""", and
            Password is - ""+pass_word+
            """
            html = """\
            <html>
            <body>
                <p>Hi,"""+name+"""<br>
                Please note your credentials for Adalat<br>
                Your <b>Email</b> is - """+email+""", and<br>
                <b>Password</b> is - """+pass_word+"""
                </p>
            </body>
            </html>
            """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            # End Mail 
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Judge')
    judge = cursor.fetchall()  
    return render_template('./admin/add-judge.html', msg=msg, username=session['username'], judge=judge)

@app.route("/admin/add-case")
def add_case_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM CasesFiled')
    file = cursor.fetchall() 
    return render_template('./admin/add-case.html',username=session['username'],file=file)

@app.route("/admin/add-case", methods=['GET', 'POST'])
def add_case():
    msg = ''
    if request.method == 'POST' and 'type' in request.form and 'details' in request.form and 'court_name' in request.form and 'hearing' in request.form:
        type = request.form['type']
        details = request.form['details']
        court_name = request.form['court_name']
        hearing = request.form['hearing']


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM `Case` WHERE type = %s AND details = %s', (type,details,))
        case = cursor.fetchone()

        if case:
            msg = 'Case already added!'
        elif not type or not details or not court_name or not hearing:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO `Case` (type,details,court_name,LastHearing,NextHearing) VALUES (%s, %s, %s, %s, %s)', (type, details, court_name, hearing, hearing,))
            mysql.connection.commit()
            msg = 'Case Added!'
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM `Case`')
    case = cursor.fetchall()  
    return render_template('./admin/add-case.html', msg=msg, username=session['username'], case=case)

### Admin Routes End ###

### Citizen Routes ###

@app.route("/citizen/view-lawyers")
def view_laywers_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Lawyer')
    lawyer = cursor.fetchall() 
    return render_template('./citizen/view-lawyers.html',uname=session['name'],lawyer=lawyer)

@app.route("/citizen/all-cases")
def view_all_cases_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT count(*) FROM `Case`')
    count = cursor.fetchone() 
    cursor.execute('SELECT * FROM `Case`')
    case = cursor.fetchall() 
    return render_template('./citizen/all-cases.html',uname=session['name'],count=count,case=case)

@app.route("/citizen/my-cases")
def my_cases_page():
    email = session['email']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT count(*) FROM `Case` WHERE ClientId = (SELECT ClientId FROM Citizen WHERE email = %s)',(email,))
    count = cursor.fetchone() 
    cursor.execute('SELECT * FROM `Case` WHERE ClientId = (SELECT ClientId FROM Citizen WHERE email = %s)',(email,))
    case = cursor.fetchall() 
    return render_template('./citizen/my-cases.html',uname=session['name'],count=count,case=case)


@app.route("/citizen/file-case")
def file_case_page():
    return render_template('./citizen/file-case.html',uname=session['name'])


@app.route("/citizen/file-case", methods=['GET', 'POST'])
def file_case():
    msg = ''
    if request.method == 'POST' and 'hcname' in request.form and 'mattert' in request.form and 'matter' in request.form and 'cname' in request.form:
        
        hcname = request.form['hcname']
        matter = request.form['matter']
        mattert = request.form['mattert']
        urgency = request.form['mattern']

        petitioner = request.form['cname']
        pdob = request.form['cdob']
        pgender = request.form['cgender']
        pphone = request.form['cphone']
        pemail = request.form['cemail']
        pstate = request.form['cstate']
        pdistrict = request.form['cdistrict']
        ppincode = request.form['cpincode']

        respondant = request.form['rname']
        rdob = request.form['rdob']
        rage = request.form['rage']
        rgender = request.form['rgender']
        rphone = request.form['rphone']
        remail = request.form['remail']
        rstate = request.form['rstate']
        rdistrict = request.form['rdistrict']
        rpincode = request.form['rpincode']

        coa = request.form['coa']
        dcoa = request.form['dcoa']
        fm = request.form['fm']
        prayer = request.form['prayer']
        grounds = request.form['grounds']
        state = request.form['state']
        district = request.form['district']

        act = request.form['act']
        acts = request.form['acts']


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM CasesFiled WHERE CourtName = %s AND Petitioner = %s', (hcname,petitioner,))
        case = cursor.fetchone()

        if case:
            msg = 'Already filed!'
        elif not hcname or not matter or not petitioner or not respondant:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO CasesFiled (CourtName,MatterNature,MatterType,Urgency,Petitioner,PDOB,PGender,PPhone,PEmail,PState,PDistrict,PPincode,Respondant,RDOB,RAge,RGender,RPhone,REmail,RState,RDistrict,RPincode,COA,DateOfCOA,FactualMatrix,Prayer,Grounds,DState,DDistrict,Act,ActSection) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)', (hcname,matter,mattert,urgency,petitioner,pdob,pgender,pphone,pemail,pstate,pdistrict,ppincode,respondant,rdob,rage,rgender,rphone,remail,rstate,rdistrict,rpincode,coa,dcoa,fm,prayer,grounds,state,district,act,acts,))
            mysql.connection.commit()
            msg = 'Filed!'
    
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    return render_template('./citizen/file-case.html',uname=session['name'],msg=msg)


### Citizen Routes End ###


### Lawyer Routes ###
@app.route("/lawyer/my-cases")
def my_cases_lawyer():
    email = session['email']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT count(*) FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s)',(email,))
    count = cursor.fetchone() 
    cursor.execute('SELECT * FROM `Case` WHERE LawyerId = (SELECT LawyerId FROM Lawyer WHERE email = %s)',(email,))
    case = cursor.fetchall() 
    return render_template('./lawyer/my-cases.html',name=session['name'],count=count,case=case)



### Lawyer Routes End ###
