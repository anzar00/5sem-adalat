from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = '23092000'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'DBAdmin@123$'
app.config['MYSQL_DB'] = 'adalat'

mysql = MySQL(app)

#Total Lawyers 
def total_lawyers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT COUNT(*) FROM Lawyer')
    count = cursor.fetchone()
    print (count)

total_lawyers

