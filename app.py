from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'our_secret_key'

#===================FUNCTIONS===================
#use this when want to test result on terminal
def checking(output):
    print("-> " + output)

#KIV : later setup database kat sini
def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_user_db():
    conn = get_db_connection('user.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

#=====================PAGES======================
#LOGIN 
@app.route('/', methods=['GET','POST'])
def login():
    checking(f"[LOGIN SCREEN]")
    if request.method == 'POST': #request the method. POST = button clicked
        name = request.form['username'].strip() #request from form,of the name 'username' #strip removes unnecessary space
        password = request.form['password'].strip()

        #KIV : setup database for users here
        # conn = get_db_connection('user.db')
        # c = conn.cursor()
        # c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        # user = c.fetchone()
        # conn.close()

        #temporary for testing only
        # if name == "admin" and password == "1234":
        user = True
        # else:
        #     user = False

        if user:
            session['username'] = name #set current user
            checking(f"Logging in {name}...") #checking
            return redirect(url_for('event_org')) #switch to 'event-org' fx
        else:
            flash("Invalid username or password. Please try again.", "error") #print out error on screen
            checking(f"Credentials unmatched. Try again.")
            return redirect(url_for('login')) #refresh the login fx
    return render_template('index.html') #initialise the screen

#REGISTRATION
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register-donor', methods=['GET','POST'])
def reg_donor():
    if request.method=='POST':
         name = request.form['name']
         email = request.form['email']
         password = request.form['password']
         contactNum = request.form['contactnum']

         checking(f"Donor name : {name} ")
         checking(f"Email : {email} ")
         checking(f"Password : {password} ")
         checking(f"Contact number : {contactNum} ")

         submit = True
         if submit:
              return redirect(url_for('login'))
         else:
              return redirect(url_for('reg_donor'))
    return render_template('register-donor.html')

@app.route('/register-eventorg', methods=['GET','POST'])
def reg_eventorg():
    if request.method=='POST':
         name = request.form['name']
         email = request.form['email']
         password = request.form['password']
         contactNum = request.form['contactnum']

         checking(f"Organizer name : {name} ")
         checking(f"Email : {email} ")
         checking(f"Password : {password} ")
         checking(f"Contact number : {contactNum} ")

         submit = True
         if submit:
              return redirect(url_for('login'))
         else:
              return redirect(url_for('reg_eventorg'))
    return render_template('register-eventorg.html')

#FORGOT PASSWORD
@app.route('/forgot-pass', methods=['GET','POST'])
def forgot_pass():
    return render_template('forgot-pass.html')

#EVENT ORGANISER
@app.route('/event-org')
def event_org():
        return render_template('event-org.html') #initialise the screen

@app.route('/create-event', methods=['GET','POST'])
def create_event():
    if request.method == 'POST':
        eventName = request.form['event-name']
        description = request.form['description']
        eventDate = request.form['date']
        location = request.form['location']
        availableSlots = request.form['slot']

        checking(f"Event name : {eventName} ")
        checking(f"Description : {description}")
        checking(f"Date : {eventDate}")
        checking(f"Location : {location}")
        checking(f"Available slots : {availableSlots}")

        triggered = True
        if triggered:
                flash("Event created! Pending admin's approval..","success")
                return redirect(url_for('create_event'))
        else:
                flash("Not triggered","error")
                return redirect(url_for('create_event'))


    return render_template('create-event.html')

#HOSPITAL
@app.route('/hospital')
def hospital():
    return render_template('hospital.html')


@app.route('/update-inv', methods=['GET','POST'])
def update_inventory():
    return render_template('update-inv.html')


@app.route('/request', methods=['GET','POST'])
def send_request():
    return render_template('request.html')

#INIT 
if __name__ == '__main__':
    app.run(debug=True)