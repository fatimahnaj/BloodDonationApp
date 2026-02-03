import sqlite3

def build_database():
    try:
        # Connect to the database, it will create the file if it is not yet exist
        connection = sqlite3.connect('database.db')
        
        # Open and read the SQL file
        with open('database.sql', 'r') as f:
            sql_script = f.read()
        
        # Execute the script
        connection.executescript(sql_script)

        # Test Run the specific Donor Test Data
        test_data = """
        INSERT INTO RegisteredUser VALUES ('D101', 'Test Donor', 'donor@mmu.edu.my', '1234', 'Donor');
        INSERT INTO Donor VALUES ('D101', '012-9998888', 'O+', 1, '1998-05-15', 'Female');
        INSERT INTO RegisteredUser VALUES ('EO01', 'MMU Red Cross', 'redcross@mmu.my', '1234', 'EO');
        INSERT INTO EventOrganiser VALUES ('EO01', 'MMU Red Cross Society', '03-83125000');
        INSERT INTO DonationEvent VALUES ('EV_FEB', 'MMU Cyberjaya Blood Drive', '2026-03-05', 'MPH MMU', 'Annual donation drive for students.', 'EO01', 50, 'Approved');
        INSERT INTO RegisteredUser VALUES ('HOSP01', 'Hospital Admin', 'hosp@cyberjaya.my', '1234', 'Hospital');
        INSERT INTO Hospital VALUES ('HOSP01', 'Hospital Cyberjaya');
        INSERT INTO UrgentRequest VALUES ('REQ_99', 'HOSP01', 'O+', 1, 3);
        INSERT INTO RegisteredUser VALUES ('ADM001', 'Hani', 'iswahani@gmail.com', 'hani05', 'Admin');
        INSERT INTO Admin VALUES ('ADM001');
        INSERT INTO DonationEvent VALUES ('EV_1', 'Life Saver Campaign', '2026-03-22', 'Sunway Pyramid Hall', 'Blood donation event occurring in Sunway Pyramid.', 'EO01', 50, 'Pending');
        """
        connection.executescript(test_data)
        
        connection.commit()
        connection.close()
        print("Successfully built the database and created tables!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    build_database()