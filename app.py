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
@app.route('/login', methods=['GET','POST'])
def login():
    checking(f"[LOGIN SCREEN]")
    if request.method == 'POST': #request the method. POST = button clicked
        username = request.form['username'].strip() #request from form,of the name 'username' #strip removes unnecessary space
        password = request.form['password'].strip()

        #KIV : setup database for users here
        # conn = get_db_connection('user.db')
        # c = conn.cursor()
        # c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        # user = c.fetchone()
        # conn.close()

        #temporary for testing only
        if username == "admin" and password == "1234":
            user = True
        else:
            user = False

        if user:
            session['username'] = username #set current user
            checking(f"Logging in {username}...") #checking
            return redirect(url_for('event_org')) #switch to 'event-org' fx
        else:
            flash("Invalid username or password. Please try again.", "error") #print out error on screen
            checking(f"Credentials unmatched. Try again.")
            return redirect(url_for('login')) #refresh the login fx
    return render_template('index.html') #initialise the screen

@app.route('/register')
def register():
    return render_template('register.html')

#EVENT ORGANISER
@app.route('/event-org')
def event_org():
        return render_template('event-org.html') #initialise the screen

@app.route('/create-event', methods=['GET','POST'])
def create_event():
    return render_template('create-event.html')



#INIT 
if __name__ == '__main__':
    app.run(debug=True)