from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd
import pickle
#from main import pipe

app = Flask(__name__)
pipe = pickle.load(open("gb_model.pkl","rb"))
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Initialize the MySQL extension
mysql = MySQL(app)


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cur.fetchone()
        cur.close()  # Close the cursor after fetching data
        if user:
            # session['loggedin'] = True
            # session['userid'] = user['userid']
            # session['name'] = user['name']
            # session['email'] = user['email']
            # message = 'Logged in successfully!'
            return render_template('index.html')
        else:
            message = 'Please enter correct email/password!'
    return render_template('login.html', message=message)


@app.route('/predict', methods=['POST'])
def predict():
    cgpa = request.form.get('cgpa')
    ip = request.form.get('ip')
    pr = request.form.get('pr')
    wc = request.form.get('wc')
    ass = request.form.get('ass')
    sst = request.form.get('sst')
    sscm = request.form.get('sscm')
    hscm = request.form.get('hscm')
    exa = request.form.get('exa')
    pt = request.form.get('pt')

    print(cgpa, ip, pr, wc, ass, sst, exa, pt, sscm, hscm)
    input = pd.DataFrame([[cgpa, ip, pr, wc, ass, sst, exa, pt, sscm, hscm]],
                         columns=['CGPA', 'Internships', 'Projects', 'Workshops/Certifications', 'AptitudeTestScore',
                                  'SoftSkillsRating', 'ExtracurricularActivities', 'PlacementTraining', 'SSC_Marks',
                                  'HSC_Marks'])
    prediction = pipe.predict(input)[0]

    if prediction == 1:
        x = "yes"
    else:
        x = "No"
    return render_template("index.html", prediction_text="Chance for placement : {}".format(x))
    # return render_template("pop.html", prediction_text = "Chance for placement : {}".format(np.round(prediction,0)))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cur.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not name or not password or not email:
            message = 'Please fill out the form!'
        else:
            cur.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (name, email, password,))
            # cur.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (name, email, password,))
            mysql.connection.commit()
            message = 'You have successfully registered!'
            cur.close()  # Close the cursor after committing changes
    return render_template('register.html', message=message)


if __name__ == "__main__":
    app.debug = True
    app.run()
