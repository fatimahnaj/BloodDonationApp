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

#DATABASE
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
#=====================PAGES======================
#LOGIN 
@app.route('/', methods=['GET','POST'])
def login():
    checking(f"[LOGIN SCREEN]")
    if request.method == 'POST': #request the method. POST = button clicked
        email_val = request.form['email'].strip() #request from form,of the name 'username' #strip removes unnecessary space
        password_val = request.form['password'].strip()

        #KIV : setup database for users here
        # conn = get_db('user.db')
        # c = conn.cursor()
        # c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        # user = c.fetchone()
        db = get_db()
        #select the 'role' along with other user data
        user = db.execute("SELECT * FROM RegisteredUser WHERE email=? AND password=?", 
                          (email_val, password_val)).fetchone()
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
            session['username'] = user['name']
            session['ID'] = user['userID']
            
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
            flash("Invalid email or password. Please try again.", "error") #print out error on screen
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
         gender = request.form.get('gender')
         dateOfBirth = request.form.get('dateOfBirth')
         bloodType = request.form.get('bloodType')
         temp_rhFactor = request.form.get('rhFactor')
         if temp_rhFactor=="pos":
             rhFactor = True
         else:
             rhFactor = False

        #make sure all details are entered
         if not name or not email or not password:
            flash("⚠️ Please fill in all fields.", "error")
            return redirect(url_for('reg_donor'))
         
         #save new registered user
         conn = get_db()
         c = conn.cursor()
         c.execute("SELECT * FROM RegisteredUser WHERE email = ?", (email,))
         if c.fetchone():
            conn.close()
            flash("❌ Email already exists. Please choose another.", "error")
            return redirect(url_for('reg_donor'))

         try:
            # Generate new userID with format D### (D101, D102, etc.)
            # Use numeric MAX on the numeric suffix to avoid lexicographic ordering and mixed prefixes
            c.execute("SELECT MAX(CAST(SUBSTR(userID, 2) AS INTEGER)) FROM RegisteredUser WHERE userID LIKE 'D%'")
            row = c.fetchone()
            max_num = row[0] if row else None

            if max_num and isinstance(max_num, int) and max_num >= 0:
                new_num = max_num + 1
            else:
                # If no D-prefixed IDs exist or parsing fails, start at 101
                new_num = 101

            user_id = f"D{new_num}"

            # Insert into RegisteredUser table with userID
            c.execute("INSERT INTO RegisteredUser (userID, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
                    (user_id, name, email, password, 'Donor'))
            # Insert into Donor table
            c.execute("INSERT INTO Donor (userID, gender, bloodType, rhFactor, contactNum, dateOfBirth) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, gender, bloodType, rhFactor, contactNum, dateOfBirth))
            conn.commit()
              
            checking(f"Donor name : {name} ")
            checking(f"Email : {email} ")
            checking(f"Password : {password} ")
            checking(f"Contact number : {contactNum} ")
            checking(f"Blood type : {bloodType}{rhFactor}")
            checking(f"User ID assigned : {user_id}")
              
            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
         except Exception as e:
            conn.rollback()
            checking(f"Error: {e}")
            flash("❌ Registration failed. Please try again.", "error")
            return redirect(url_for('reg_donor'))
         finally:
            conn.close()
              
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

        #make sure all details are entered
         if not name or not email or not password:
            flash("⚠️ Please fill in all fields.", "error")
            return redirect(url_for('reg_donor'))
         
         #save new registered user
         conn = get_db()
         c = conn.cursor()
         c.execute("SELECT * FROM RegisteredUser WHERE email = ?", (email,))
         if c.fetchone():
            conn.close()
            flash("❌ Email already exists. Please choose another.", "error")
            return redirect(url_for('reg_donor'))

         try:
            # Generate new userID with format D### (D101, D102, etc.)
            # Use numeric MAX on the numeric suffix to avoid lexicographic ordering and mixed prefixes
            c.execute("SELECT MAX(CAST(SUBSTR(userID, 2) AS INTEGER)) FROM RegisteredUser WHERE userID LIKE 'EO%'")
            row = c.fetchone()
            max_num = row[0] if row else None

            if max_num and isinstance(max_num, int) and max_num >= 0:
                new_num = max_num + 1
            else:
                # If no EO-prefixed IDs exist or parsing fails, start at 1
                new_num = 1

            user_id = f"EO{new_num}"

            # Insert into RegisteredUser table with userID
            c.execute("INSERT INTO RegisteredUser (userID, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
                    (user_id, name, email, password, 'EO'))
            c.execute("INSERT INTO EventOrganiser (userID, companyName, contactNum) VALUES (?, ?, ?)",
                    (user_id, name, contactNum))
            conn.commit()
              
            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
         except Exception as e:
            conn.rollback()
            checking(f"Error: {e}")
            flash("❌ Registration failed. Please try again.", "error")
            return redirect(url_for('reg_eventorg'))
         finally:
            conn.close()
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

#DONOR 

#donor-dashboard
@app.route('/donor-dashboard')
def donor_dashboard():
    #check session to make sure only logged in donors can see this
    if 'username' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
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
    
    user_id = session['ID']
    db = get_db()

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

    db = get_db()
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

    db = get_db()
    
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

