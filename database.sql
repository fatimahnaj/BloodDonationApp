DROP TABLE IF EXISTS Appointment;
DROP TABLE IF EXISTS Feedback;
DROP TABLE IF EXISTS UrgentRequest;
DROP TABLE IF EXISTS BloodInventory;
DROP TABLE IF EXISTS DonationEvent;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Hospital;
DROP TABLE IF EXISTS EventOrganiser;
DROP TABLE IF EXISTS Donor;
DROP TABLE IF EXISTS RegisteredUser;

CREATE TABLE RegisteredUser (
    userID VARCHAR(20) NOT NULL,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL, -- Encrypted credentials
    role VARCHAR(15) NOT NULL, -- Donor, EO, Staff, Admin 
    PRIMARY KEY (userID)
);

CREATE TABLE Donor (
    userID VARCHAR(20) NOT NULL,
    contactNum VARCHAR(15) NOT NULL,
    bloodType VARCHAR(10) NOT NULL,
    RhFactor BOOLEAN NOT NULL,
    dateOfBirth VARCHAR(10) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    PRIMARY KEY (userID),
    FOREIGN KEY (userID) REFERENCES RegisteredUser(userID)
);

CREATE TABLE EventOrganiser (
    userID VARCHAR(20) NOT NULL,
    companyName VARCHAR(100) NOT NULL,
    contactNum VARCHAR(15) NOT NULL,
    PRIMARY KEY (userID),
    FOREIGN KEY (userID) REFERENCES RegisteredUser(userID)
);

CREATE TABLE Hospital (
    userID VARCHAR(20) NOT NULL,
    hospitalName VARCHAR(100) NOT NULL,
    PRIMARY KEY (userID),
    FOREIGN KEY (userID) REFERENCES RegisteredUser(userID)
);

CREATE TABLE Admin (
    userID VARCHAR(20) NOT NULL,
    PRIMARY KEY (userID),
    FOREIGN KEY (userID) REFERENCES RegisteredUser(userID)
);


CREATE TABLE DonationEvent (
    eventID VARCHAR(20) NOT NULL,
    eventName VARCHAR(100) NOT NULL,
    eventDate DATE NOT NULL,
    eventLocation VARCHAR(20) NOT NULL,
    description VARCHAR(50) NOT NULL,
    userID VARCHAR(20) NOT NULL, -- Links to EventOrganiser 
    availableSlots INT NOT NULL,
    status VARCHAR(15) NOT NULL, -- Pending, Approved, Rejected 
    PRIMARY KEY (eventID),
    FOREIGN KEY (userID) REFERENCES EventOrganiser(userID)
);

CREATE TABLE Appointment (
    appointmentID VARCHAR(20) NOT NULL,
    userID VARCHAR(20) NOT NULL, -- Links to Donor 
    eventID VARCHAR(20) NOT NULL,
    appointmentDate VARCHAR(10) NOT NULL,
    confirmationStatus VARCHAR(15) NOT NULL, -- Confirmed or Cancelled 
    PRIMARY KEY (appointmentID),
    FOREIGN KEY (userID) REFERENCES Donor(userID),
    FOREIGN KEY (eventID) REFERENCES DonationEvent(eventID)
);

CREATE TABLE Feedback (
    feedbackID VARCHAR(20) NOT NULL,
    userID VARCHAR(20) NOT NULL, -- Links to Donor
    eventID VARCHAR(20) NOT NULL,
    rating FLOAT NOT NULL,
    comment VARCHAR(255), -- Optional field 
    PRIMARY KEY (feedbackID),
    FOREIGN KEY (userID) REFERENCES Donor(userID),
    FOREIGN KEY (eventID) REFERENCES DonationEvent(eventID)
);

CREATE TABLE BloodInventory (
    inventoryID VARCHAR(20) NOT NULL,
    userID VARCHAR(20) NOT NULL, -- Links to Hospital
    bloodType VARCHAR(10) NOT NULL,
    currentStock INT NOT NULL,
    PRIMARY KEY (inventoryID),
    FOREIGN KEY (userID) REFERENCES Hospital(userID)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory
ON BloodInventory(inventoryID);

CREATE TABLE UrgentRequest (
    requestID VARCHAR(20) NOT NULL,
    userID VARCHAR(20) NOT NULL, -- Links to Hospital 
    requiredBloodType VARCHAR(10) NOT NULL,
    RhesusFactor BOOLEAN NOT NULL,
    urgencyLevel INT NOT NULL, -- 1 (Low) to 3 (Extreme) 
    PRIMARY KEY (requestID),
    FOREIGN KEY (userID) REFERENCES Hospital(userID)
);

CREATE TABLE IF NOT EXISTS Notifications (
    notificationID VARCHAR(20) NOT NULL PRIMARY KEY,
    userID VARCHAR(20) NOT NULL,   -- Donor who will receive this
    hospitalID VARCHAR(20) NOT NULL,  -- Who sent the request
    message TEXT NOT NULL,
    requestID VARCHAR(20) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES Donor(userID),
    FOREIGN KEY (hospitalID) REFERENCES Hospital(userID),
    FOREIGN KEY (requestID) REFERENCES UrgentRequest(requestID)
);