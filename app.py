from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
import datetime

app = Flask(__name__)
app.secret_key = 'our_secret_key'
app.secret_key = 'mmu_blood_donation_key'

#===================FUNCTIONS===================
#use this when want to test result on terminal
def checking(output):
    print("-> " + output)

#KIV : later setup database kat sini
def get_db_connection(db_name='database.db'):
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
        username_val = request.form['username'].strip() #request from form,of the name 'username' #strip removes unnecessary space
        password_val = request.form['password'].strip()

        #KIV : setup database for users here
        # conn = get_db_connection('user.db')
        # c = conn.cursor()
        # c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        # user = c.fetchone()
        db = get_db_connection()
        #select the 'role' along with other user data
        user = db.execute("SELECT * FROM RegisteredUser WHERE userID=? AND password=?", 
                          (username_val, password_val)).fetchone()
        db.close()

        #temporary for testing only
        #if username == "admin" and password == "1234":
        #    user = True
        #else:
        #   user = False

        #if user:
        #    session['username'] = username #set current user
        #    checking(f"Logging in {username}...") #checking
        #    return redirect(url_for('event_org')) #switch to 'event-org' fx

        #if the data is found in the database, we SAVE their ID in the sessions(cookies)
        if user:
            session['username'] = user['userID']
            
            # Role-Based Redirection Logic, send actors to their pages
            if user['role'] == 'Donor':
                return redirect(url_for('donor_dashboard'))
            elif user['role'] == 'EO':
                return redirect(url_for('event_org'))
            elif user['role'] == 'Hospital':
                return redirect(url_for('hospital'))
            else:
                # Default fallback (e.g., for Admin)
                return redirect(url_for('event_org'))
        else:
            #if user credentials is invalid
            flash("Invalid username or password. Please try again.", "error") #print out error on screen
            checking(f"Credentials unmatched. Try again.")
            return redirect(url_for('login')) #refresh the login fx
    return render_template('index.html') #initialise the screen

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

#DONOR 

#donor-dashboard
@app.route('/donor-dashboard')
def donor_dashboard():
    #check session to make sure only logged in donors can see this
    if 'username' not in session:
        return redirect(url_for('login'))
    
    db = get_db_connection()
    #for view events, ONLY fetch events if 'Approved'by admin
    events = db.execute("SELECT * FROM DonationEvent WHERE status = 'Approved'").fetchall()

    #for view notifications, fetch urgent request by hospital
    notifications = db.execute('''
        SELECT Hospital.hospitalName, UrgentRequest.requiredBloodType 
        FROM UrgentRequest 
        JOIN Hospital ON UrgentRequest.userID = Hospital.userID
    ''').fetchall()
    db.close()
    return render_template('donor-dashboard.html', events=events, notifications=notifications)

#donor-profile
@app.route('/donor-profile', methods=['GET', 'POST'])
def donor_profile():
    #check session to make sure only logged in donors can see this
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user_id = session['username']
    db = get_db_connection()

    # If the user clicks edit to update their donor profile
    if request.method == 'POST':
        try:
            email = request.form['email']
            phone = request.form['contactNum']
            dob = request.form['dob']
            
            # Simple validation, heck if email or phone field is empty
            if not email or not phone:
                flash("Update failed: Email and Contact Number are required.", "error")
            else:
                db.execute("UPDATE RegisteredUser SET email = ? WHERE userID = ?", (email, user_id))
                db.execute("UPDATE Donor SET contactNum = ?, dateOfBirth = ? WHERE userID = ?", (phone, dob, user_id))
                db.commit()
                flash("Profile updated successfully!", "success")
        finally:
            db.close() 
        return redirect(url_for('donor_profile'))

    # Handling the GET request to fill the fields in the form (Page Refresh)
    try:
    #fetch user data for the profile card
        row = db.execute('''
            SELECT u.name, u.email, d.gender, d.bloodType, d.contactNum, d.dateOfBirth 
            FROM RegisteredUser u 
            JOIN Donor d ON u.userID = d.userID 
            WHERE u.userID = ?''', (user_id,)).fetchone()
    
    #fetch notification
        notifications = db.execute('''
            SELECT Hospital.hospitalName, UrgentRequest.requiredBloodType 
            FROM UrgentRequest 
            JOIN Hospital ON UrgentRequest.userID = Hospital.userID
        ''').fetchall()
    finally:
        db.close()
    
    #passing both user and notifications to the template
    return render_template('donor-profile.html', user=row, notifications=notifications)

#feedback page   
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    user_id = session['username']  

    if request.method == 'POST':
        try:
            #feedback form fields to fill
            rating = request.form.get('rating')
            comment = request.form.get('comment')

            db.execute('''INSERT INTO Feedback (userID, rating, comment) 
                          VALUES (?, ?, ?, ?, ?)''', 
                       (user_id, rating, comment))
            db.commit()
            flash("Feedback submitted!", "success")
        finally:
            db.close()
        return redirect(url_for('donor_dashboard'))

    #notifications for the bell icon
    notifications = db.execute('''
        SELECT Hospital.hospitalName, UrgentRequest.requiredBloodType 
        FROM UrgentRequest 
        JOIN Hospital ON UrgentRequest.userID = Hospital.userID
    ''').fetchall()
    db.close()
    return render_template('feedback.html', notifications=notifications)

#book appointment button 
@app.route('/book-event/<eventID>', methods=['POST'])
def book_event(eventID):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_id = session['username']
    # Generate a unique appointmentID for booking using current time
    appointment_id = "AP" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    db = get_db_connection()
    
    #validation for donor book appointment
    try:
        #check for duplicate (if user already book the same event)
        existing = db.execute("SELECT * FROM Appointment WHERE userID=? AND eventID=?", (user_id, eventID)).fetchone()
        if existing:
            flash("You have already booked this event.", "warning")
            return redirect(url_for('donor_dashboard'))

        #check if there are slots left (slots > 0)
        event = db.execute("SELECT availableSlots FROM DonationEvent WHERE eventID=?", (eventID,)).fetchone()
        if event and event['availableSlots'] > 0:
            #insert booking records
            db.execute('''INSERT INTO Appointment 
                          (appointmentID, userID, eventID, appointmentDate, confirmationStatus) 
                          VALUES (?, ?, ?, ?, ?)''', 
                       (appointment_id, user_id, eventID, current_date, 'Confirmed'))
            #subtract 1 from the available slots.
            db.execute("UPDATE DonationEvent SET availableSlots = availableSlots - 1 WHERE eventID = ?", (eventID,))
            db.commit()
            flash("Appointment booked successfully!", "success")
        else:
            flash("Event is full.", "error")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        flash("System error. Please contact admin.", "error")
    finally:
        db.close()
    return redirect(url_for('donor_dashboard'))

#INIT 
if __name__ == '__main__':
    app.run(debug=True)

