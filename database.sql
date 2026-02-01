CREATE TABLE RegisteredUser (
    userID VARCHAR(20) NOT NULL,
    name VARCHAR(50) NOT NULL
    email VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL, -- Encrypted credentials
    role VARCHAR(15) NOT NULL, -- Donor, EO, Staff, Admin 
    PRIMARY KEY (userID)
)

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

CREATE TABLE UrgentRequest (
    requestID VARCHAR(20) NOT NULL,
    userID VARCHAR(20) NOT NULL, -- Links to Hospital 
    requiredBloodType VARCHAR(10) NOT NULL,
    RhesusFactor BOOLEAN NOT NULL,
    urgencyLevel INT NOT NULL, -- 1 (Low) to 3 (Extreme) 
    PRIMARY KEY (requestID),
    FOREIGN KEY (userID) REFERENCES Hospital(userID)
);

