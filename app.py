from flask import Flask, render_template, request, redirect, url_for, session, flash 
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import sqlite3, os
import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'mmu_blood_donation_key'

#===================FUNCTIONS===================
#EMAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fatimahnajihah05@gmail.com'
app.config['MAIL_PASSWORD'] = 'kdtg gpki efah gyal'  # NOT gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

#TOKEN ----------
serializer = URLSafeTimedSerializer(app.secret_key)

#use this when want to test result on terminal
def checking(output):
    print("-> " + output)

#DATABASE
def get_db():
    conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
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

        db = get_db()
        #select the 'role' along with other user data
        user = db.execute("SELECT * FROM RegisteredUser WHERE email=? AND password=?", 
                          (email_val, password_val)).fetchone()
        db.close()

        #if the data is found in the database, we SAVE their ID in the sessions(cookies)
        if user:
            session['username'] = user['name']
            session['ID'] = user['userID']
            session['role'] = user['role']

            # Role-Based Redirection Logic, send actors to their pages
            if user['role'] == 'Donor':
                return redirect(url_for('donor_dashboard'))
            elif user['role'] == 'EO':
                return redirect(url_for('event_org'))
            elif user['role'] == 'Hospital':
                return redirect(url_for('hospital'))
            elif user['role'] == 'Admin':
               return redirect(url_for('admin_dashboard'))
            else:
                flash("Unknown role.", "error")
                return redirect(url_for('login'))    
        
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
    if request.method == 'POST':
        email = request.form['email'].strip()

        # TEMP: pretend email exists
        user_exists = True  

        if user_exists:
            token = serializer.dumps(email, salt='password-reset')
            reset_link = url_for('reset_password', token=token, _external=True)

            msg = Message("Password Reset Request")
            msg.body = f"Click the link to reset your password:\n{reset_link}"
            msg.recipients = [email]

            mail.send(msg)

            flash("Password reset link sent to your email.", "success")
            return redirect(url_for('login'))

        flash("Email not found.", "error")
    return render_template('forgot-pass.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except:
        flash("Invalid or expired link.", "error")
        return redirect(url_for('forgot_pass'))

    if request.method == 'POST':
        new_password = request.form['password']

        # UPDATE DATABASE HERE
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute("UPDATE RegisteredUser SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            print(f"Password reset for {email}")
            flash("Password updated successfully.", "success")
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('reset-pass.html', token=token)


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

        #make sure all details are entered
        if not eventName or not eventDate or not location or not availableSlots:
            flash("⚠️ Please fill in all fields.", "error")
            return redirect(url_for('create_event'))
        
        checking(f"Event name : {eventName} ")
        checking(f"Description : {description}")
        checking(f"Date : {eventDate}")
        checking(f"Location : {location}")
        checking(f"Available slots : {availableSlots}")


        conn = get_db()
        c = conn.cursor()

        # Generate auto-incrementing eventID with format EV_test# (EV_test1, EV_test2, etc.)
        c.execute("SELECT MAX(CAST(SUBSTR(eventID, 8) AS INTEGER)) FROM DonationEvent WHERE eventID LIKE 'EV_%'")
        row = c.fetchone()
        max_num = row[0] if row else None

        if max_num and isinstance(max_num, int) and max_num >= 0:
            new_num = max_num + 1
        else:
            # If no EV_test-prefixed IDs exist, start at 1
            new_num = 1

        event_id = f"EV_test{new_num}"
        try:
            c.execute("INSERT INTO DonationEvent (eventID,eventName,eventDate,eventLocation,description,userID,availableSlots,status) VALUES (?,?,?,?,?,?,?,?)",
                      (event_id,eventName,eventDate,location,description,session['ID'],availableSlots,'Pending'))
            conn.commit()
            flash("Event created! Pending admin's approval..","success")
            return redirect(url_for('create_event'))
        except Exception as e:
            conn.rollback()
            checking(f"Error: {e}")

            flash("Not triggered","error")
            return redirect(url_for('create_event'))
        finally:
            conn.close()

    return render_template('create-event.html')

#HOSPITAL
@app.route('/hospital')
def hospital():
    return render_template('hospital.html')

@app.route('/update-inv', methods=['GET','POST'])
def update_inventory():

    if request.method == 'POST':
        try:
            db = get_db()

            user_id = session.get('ID')

            blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

            for t in blood_types:
                qty = request.form.get(t.replace("+", "_pos").replace("-", "_neg"))

                if qty is not None and qty != "":

                    inventory_id = f"INV_{user_id}_{t}"

                    db.execute("""
                        INSERT INTO BloodInventory (inventoryID, userID, bloodType, currentStock)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(inventoryID)
                        DO UPDATE SET currentStock=excluded.currentStock
                    """, (inventory_id, user_id, t, qty))

            db.commit()
            flash("Inventory updated successfully!", "success")

        except Exception as e:
            print("ERROR:", e)
            flash(str(e), "error")

        finally:
            db.close()

        return redirect(url_for('update_inventory'))

    return render_template('update-inv.html')

@app.route('/request', methods=['GET','POST'])
def send_request():

    if "ID" not in session:
        flash("Please login as hospital first.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':

        blood = request.form.get('blood_type')  # Returns None if nothing is selected
        rh = request.form.get('rh')
        urgency = request.form.get('urgency')

        if not blood or not rh or not urgency:
            flash("Please fill in all fields.", "error")
            return redirect(url_for('send_request'))


        rhesus = 1 if rh == '+' else 0

        level = {
            "normal": 1,
            "high": 2,
            "critical": 3
        }[urgency]

        requestID = "REQ_" + str(uuid.uuid4())[:8]
        hospitalID = session.get("ID")

        conn = get_db()

        conn.execute("""
            INSERT INTO UrgentRequest
            (requestID, userID, requiredBloodType, RhesusFactor, urgencyLevel)
            VALUES (?, ?, ?, ?, ?)
        """, (requestID, hospitalID, blood, rhesus, level))

        matching_donors = conn.execute("""
            SELECT userID FROM Donor
            WHERE bloodType = ? AND rhFactor = ?
        """, (blood, bool(rhesus))).fetchall()

        for donor in matching_donors:
            notificationID = "NOTIF_" + str(uuid.uuid4())[:8]
            message = f"Urgent blood request: {blood}{'+' if rhesus else '-'}"
            conn.execute("""
                INSERT INTO Notifications (notificationID, userID, hospitalID, message, requestID)
                VALUES (?, ?, ?, ?, ?)
            """, (notificationID, donor['userID'], hospitalID, message, requestID))

        conn.commit()
        conn.close()

        flash("Urgent request sent!", "success")
        return redirect(url_for('hospital'))

    return render_template('request.html')

#DONOR 

#donor-dashboard
@app.route('/donor-dashboard')
def donor_dashboard():
    #check session to make sure only logged in donors can see this
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_id = session['ID']
    
    db = get_db()
    #for view events, ONLY fetch events if 'Approved'by admin
    events = db.execute("SELECT * FROM DonationEvent WHERE status = 'Approved'").fetchall()
    
    donor = db.execute("SELECT bloodType, RhFactor FROM Donor WHERE userID = ?", (user_id,)).fetchone()
    donor_blood = donor['bloodType']
    donor_rh = donor['RhFactor']
    
    #fetch ID of events this specific user has already booked
    user_bookings = db.execute("SELECT eventID FROM Appointment WHERE userID = ?", (user_id,)).fetchall()

    #create a simple list of those IDs 
    booked_event_ids = [str(b['eventID']) for b in user_bookings]

    #for view notifications, fetch urgent request by hospital
    notifications = db.execute('''
        SELECT Hospital.hospitalName, UrgentRequest.requiredBloodType, UrgentRequest.urgencyLevel
        FROM UrgentRequest 
        JOIN Hospital ON UrgentRequest.userID = Hospital.userID
        WHERE UrgentRequest.requiredBloodType = ? AND UrgentRequest.RhesusFactor = ?
        ORDER BY UrgentRequest.urgencyLevel DESC, UrgentRequest.requestID DESC
    ''',(donor_blood, donor_rh)).fetchall()
    
    db.close()

    #pass the 'booked_event_ids' list to the donor-dashboard.html
    return render_template('donor-dashboard.html', events=events, notifications=notifications, booked_ids=booked_event_ids)

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
@app.route('/feedback/<event_id>', methods=['GET', 'POST'])
def feedback(event_id):
    if 'ID' not in session:
        return redirect(url_for('login'))

    db = get_db()
    user_id = session.get('ID')

    if request.method == 'POST':
        try:
            #feedback form fields to fill
            rating = request.form.get('rating')
            comment = request.form.get('comment')

            # Generate a simple unique ID for the feedback
            feedback_id = "FB" + str(uuid.uuid4())[:8]

            db.execute('''INSERT INTO Feedback (feedbackID, userID, eventID, rating, comment) 
                        VALUES (?, ?, ?, ?, ?)''', 
                       (feedback_id, user_id, event_id, rating, comment))
            db.commit()
            flash("Feedback submitted! Thank you!", "success")
        except Exception as e:
            checking(f"Feedback Error: {e}")
            flash("Error submitting feedback.", "error")

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
    
    user_id = session['ID']
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

#admin_dahsboard
@app.route('/admin_dashboard')
def admin_dashboard():
    #Verification: Ensure user is an Admin
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db()
    
    # Metric: Total Blood Volume Collected
    total_vol = conn.execute('SELECT SUM(currentStock) FROM BloodInventory').fetchone()[0] or 0
    
    # Metric: Total unique donor participation 
    donor_count = conn.execute('SELECT COUNT(DISTINCT userID) FROM Appointment').fetchone()[0] or 0
    
    # Metric: Identify top-performing event based on ratings 
    top_event_row = conn.execute(''' SELECT de.eventName, AVG(f.rating) AS avg_rating FROM DonationEvent de JOIN Feedback f ON de.eventID = f.eventID
    GROUP BY de.eventID ORDER BY avg_rating DESC LIMIT 1 ''').fetchone()

    top_event_name = top_event_row[0] if top_event_row else "N/A"
    top_event_rating = top_event_row[1] if top_event_row else 0


    conn.close()
    
    # Render the report interface
    return render_template('admin_dashboard.html', 
                           name=session.get('username'),
                           vol=total_vol, 
                           donors=donor_count, 
                           top=top_event_name)

#admin_approval
@app.route("/admin_approval")
def admin_approval():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM DonationEvent WHERE status='Pending'")
    events = cur.fetchall()

    conn.close()

    return render_template(
        "admin_approval.html",
        events=events
    )

@app.route('/update_status/<eventID>/<action>')
def update_status(eventID, action):

    new_status = 'Approved' if action == 'approve' else 'Rejected'
    
    conn = get_db()

    conn.execute('UPDATE DonationEvent SET status = ? WHERE eventID = ?', (new_status, eventID))
    conn.commit()
    conn.close()
    
    # Redirect back to the approval list
    return redirect(url_for('admin_approval'))

#INIT 
if __name__ == '__main__':
    app.run(debug=True)
