CREATE TABLE Campaigns (
  campaignID  SERIAL PRIMARY KEY,
  cost DECIMAL(15, 2),
  name VARCHAR(200),
  description TEXT,
  startDate TIMESTAMP,
  endDate TIMESTAMP
);

CREATE TABLE Events (
  eventID SERIAL PRIMARY KEY,
  name VARCHAR(200),
  location VARCHAR(100),
  description TEXT,
  eventTime TIMESTAMP,
  fundraisedAmount DECIMAL(15, 2)
);

CREATE TABLE Volunteers (
  volunteerID SERIAL PRIMARY KEY,
  name VARCHAR(200),
  numParticipatedIn INTEGER,
  tier VARCHAR(50) DEFAULT 'Beginner', -- Adding default value
  contactInfo VARCHAR(50)
);

CREATE TABLE Members (
  memberID SERIAL PRIMARY KEY,
  name VARCHAR(200),
  contactInfo VARCHAR(50)
);

CREATE TABLE Donors (
  donorID SERIAL PRIMARY KEY,
  name VARCHAR(200),
  contactInfo VARCHAR(50),
  tier VARCHAR(50) CHECK (tier IN ('PLATINUM', 'GOLD', 'SILVER', 'BRONZE'))
);

CREATE TABLE Employees (
  employeeID SERIAL PRIMARY KEY,
  name VARCHAR(200),
  salary DECIMAL(15, 2)
);

CREATE TABLE WebsitePost (
  postID SERIAL PRIMARY KEY,
  postedTime TIMESTAMP,
  postSummary TEXT
);

CREATE TABLE Offices (
  location VARCHAR(100) PRIMARY KEY,
  rent DECIMAL(15, 2),
  officePhone VARCHAR(14) CHECK (officePhone like '___-___-____')
);

CREATE TABLE Expenses (
  expenseID SERIAL PRIMARY KEY,
  amount DECIMAL(15, 2),
  expenseDate TIMESTAMP,
  purpose TEXT,
  expenseType VARCHAR(75)
);

CREATE TABLE Funds (
  depositID SERIAL PRIMARY KEY,
  campaign INTEGER REFERENCES Campaigns(campaignID),
  donor INTEGER REFERENCES Donors(donorID),
  amount DECIMAL(15, 2),
  depositDate TIMESTAMP,
  paymentMethod VARCHAR(150)
);

CREATE TABLE Annotations (
    annotationID SERIAL PRIMARY KEY,
    entity_type VARCHAR(50),  -- Type of entity being annotated (e.g., Campaign, Member, etc.)
    entity_id INTEGER,        -- ID of the entity being annotated
    annotation TEXT            -- The annotation content
);

CREATE TABLE Updates (
  campaignID INTEGER REFERENCES Campaigns(campaignID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  postID INTEGER REFERENCES WebsitePost(postID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (campaignID, postID)
);


CREATE TABLE Posts (
  employeeID INTEGER REFERENCES Employees(employeeID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  postID INTEGER REFERENCES WebsitePost(postID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (employeeID, postID)
  
);

CREATE TABLE Manages (
  employeeID INTEGER REFERENCES Employees(employeeID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  campaignID INTEGER REFERENCES Campaigns(campaignID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (employeeID, campaignID)
);

CREATE TABLE Holds (
  campaign INTEGER REFERENCES Campaigns(campaignID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  event INTEGER REFERENCES Events(eventID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (campaign, event)
);


CREATE TABLE ParticipatesIn (
  campaignID INTEGER REFERENCES Campaigns(campaignID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  volunteerID INTEGER REFERENCES Volunteers(volunteerID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (campaignID, volunteerID)
);

CREATE TABLE ScheduledFor (
  volunteerID INTEGER REFERENCES Volunteers(volunteerID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  eventID INTEGER REFERENCES Events(eventID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (volunteerID, eventID)
);

CREATE TABLE Supports (
  memberID INTEGER REFERENCES Members(memberID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  eventID INTEGER REFERENCES Events(eventID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (memberID, eventID)
);

CREATE TABLE Incurs (
  expenseID INTEGER REFERENCES Expenses(expenseID),
  location VARCHAR(100) REFERENCES Offices(location),
  campaignID INTEGER REFERENCES Campaigns(campaignID),
  employeeID INTEGER REFERENCES Employees(employeeID),
  CHECK (
    (location IS NOT NULL AND campaignID IS NULL AND employeeID IS NULL) OR
    (location IS NULL AND campaignID IS NOT NULL AND employeeID IS NULL) OR
    (location IS NULL AND campaignID IS NULL AND employeeID IS NOT NULL)
  )
);


CREATE TABLE WorksAt (
  location VARCHAR(100) REFERENCES Offices(location)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  employeeID INTEGER REFERENCES Employees(employeeID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  PRIMARY KEY (location, employeeID)
);

-- -- Check if the postedEmployee exists in the Employees table
CREATE OR REPLACE FUNCTION check_postedEmployee()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.employeeID NOT IN (SELECT employeeID FROM Employees) THEN
        -- Raise an exception
        RAISE EXCEPTION 'Employee does not exist in Employees table';
    END IF;
    
    -- If the employee exists, return the NEW row
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_postedEmployee_constraint
BEFORE INSERT OR UPDATE ON Posts
FOR EACH ROW
EXECUTE PROCEDURE check_postedEmployee();

-- set a volunteer's tier
CREATE OR REPLACE FUNCTION set_volunteer_tier()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.numParticipatedIn >= 3 THEN
        -- Assign tier based on participation
        NEW.tier := 'Experienced';
    ELSE
        NEW.tier := 'Beginner';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_volunteer_tier
BEFORE INSERT OR UPDATE ON Volunteers
FOR EACH ROW
EXECUTE PROCEDURE set_volunteer_tier();

-- Whenever a volunteer participates in a new campaign, update their participation
CREATE OR REPLACE FUNCTION update_participation()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment numParticipatedIn by 1
    UPDATE Volunteers
    SET numParticipatedIn = numParticipatedIn + 1
    WHERE volunteerID = NEW.volunteerID;

    -- Update volunteer's tier based on participation
    UPDATE Volunteers
    SET tier = CASE 
                  WHEN numParticipatedIn >= 3 THEN 'Experienced'
                  ELSE 'Beginner'
              END
    WHERE volunteerID = NEW.volunteerID;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to execute the update_participation function
CREATE TRIGGER update_participation_trigger
AFTER INSERT ON ParticipatesIn
FOR EACH ROW
WHEN (NEW.volunteerID IS NOT NULL)
EXECUTE PROCEDURE update_participation();


-- Dummy Data

INSERT INTO Campaigns(cost, description, name, startDate, endDate) VALUES
(2000, 'A Campaign with focus on preserving the island greenery, trees, and forests', 'Keep the Island Green!', '2024-04-04', '2024-05-10'),
(3500, 'A Campaign with focus on saving the local wildlife', 'WildHaven: Protecting Island Wildlife', '2024-05-15', '2024-07-15');

INSERT INTO Events(name, description, location, eventTime, fundraisedAmount) VALUES
('Sow & Grow: Island Tree Planting Rally', 'Tree Planting in Beacon Hill Park where $10 is donated for every tre planted', '100 Cook St., Victoria, BC', '2024-04-16 11:30:00', 670.00),
('CleanSteps Island Cleanup Drive', 'Trail cleanup in Victoria', 'Goldstream Provincial Park, Victoria, BC', '2024-04-20 10:25:00', 0.00),
('CleanSteps Island Cleanup Drive', 'Trail cleanup in Comox', 'Bear Creek Nature Park, Comox, BC', '2024-04-20 11:45:00', 0.00),
('Conservation Celebration Ball', 'Charity Gala to raise money towards Awareness activities', '412 Main St. Victoria, BC', '2024-05-30 17:45:00', 7625.00),
('EcoWarriors!', 'Youth Awareness event where local wildlife are introduced to students in school', '123 Elementary, Victoria, BC', '2024-05-25 12:50:00', 0.00);

INSERT INTO Holds(campaign, event) VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 4),
(2, 5);

INSERT INTO Volunteers (name, numParticipatedIn, contactInfo) VALUES
('Alice Johnson', 1, 'alice@example.com'),
('Bob Smith', 1, 'bob@example.com'),
('John Leary', 3, 'jleary@example.com'),
('Eva Martinez', 0, 'eva@example.com');

INSERT INTO ParticipatesIn(volunteerID, campaignID) VALUES
(1, 1),
(3, 1),
(4, 1),
(2, 2),
(3, 2),
(1, 2);

INSERT INTO ScheduledFor (volunteerID, eventID) VALUES
(1, 1),
(3, 1),
(4, 2),
(1, 3),
(1, 5),
(2, 4),
(3, 4);

INSERT INTO Members (name, contactInfo) VALUES
('Sarah Brown', 'sarah@example.com'),
('Bob Smith', 'bob@example.com'),
('Angela Kilman', 'kilman@example.com'),
('Mary Thera', 'thera@example.com'),
('David Wilson', 'david@example.com');

INSERT INTO Supports (memberID, eventID) VALUES
(1, 2),
(1, 5),
(2, 5);

INSERT INTO Donors (name, contactInfo, tier) VALUES
('XYZ Corporation', 'info@xyzcorp.com', 'PLATINUM'),
('ABC Corporation', 'info@abccorp.com', 'GOLD'),
('Susan Martinez', 'sMartinez@example.com', 'BRONZE'),
('Sarah Brown', 'sarah@example.com', 'BRONZE'),
('GnG', 'info@gng.com', 'SILVER');

INSERT INTO Funds (campaign, donor, amount, depositDate, paymentMethod) VALUES
(1, 1, 2000.00, '2024-04-12', 'Cheque'),
(2, 1, 1750.00, '2024-05-30', 'Cheque'),
(2, 2, 5000.00, '2024-05-30', 'Cheque'),
(2, 3, 1500.00, '2024-05-30', 'Credit Card'),
(2, 4, 500.00, '2024-05-30', 'Cash'),
(2, 5, 7625.00, '2024-05-30', 'Varied'),
(1, 5, 670.00, '2024-04-16', 'Cheque');

INSERT INTO Employees (name, salary) VALUES
('John Doe', 50000.00),
('Jane Smith', 55000.00),
('Michael Johnson', 60000.00);

INSERT INTO Manages(employeeID, campaignID) VALUES
(3, 1),
(2, 2),
(1, 2);

INSERT INTO WebsitePost (postedTime, postSummary)
VALUES
('2024-03-18 10:00:00', 'Excited to announce our new campaign "Keep the Island Green!" Check out the details.'),
('2024-03-19 11:30:00', 'Join us for the upcoming event "Sow & Grow: Island Tree Planting Rally" in Beacon Hill Park.'),
('2024-04-02 14:45:00', 'Get ready for the "CleanSteps Island Cleanup Drive" happening in Victoria and Comox.'),
('2024-05-11 09:00:00', 'Our campaign "Keep the Island Green!" has ended successfully. Thank you for your support and participation! Stay tuned for updates on our next campaign.'),
('2024-05-15 10:00:00', 'We are excited to introduce our new campaign "WildHaven: Protecting Island Wildlife"! Join us in our efforts to protect the local wildlife and preserve their habitats.'),
('2024-05-30 09:00:00', 'Join us at the "Conservation Celebration Ball" for an evening of fundraising and awareness.'),
('2024-05-25 15:30:00', 'Today we had "EcoWarriors!" event where local wildlife are introduced to students at 123 elementary. See some pics of our young eco warriors!');

INSERT INTO Posts(postID, employeeID) VALUES
(1, 1),
(2, 3),
(3, 1),
(4, 1),
(5, 3),
(6, 3),
(7, 1);

INSERT INTO Updates(postID, campaignID) VALUES
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 2),
(6, 2),
(7, 2);

INSERT INTO Offices (location, rent, officePhone) VALUES
('123 Main St, Victoria, BC', 2500.00, '123-456-7890');

INSERT INTO WorksAt(location, employeeID) VALUES
('123 Main St, Victoria, BC', 1),
('123 Main St, Victoria, BC', 2),
('123 Main St, Victoria, BC', 3);

INSERT INTO Expenses (amount, expenseDate, purpose, expenseType) VALUES
(500.00, '2024-04-16', 'Catering for Sow & Grow: Island Tree Planting Rally', 'Event Catering'),
(300.00, '2024-04-20', 'Transportation for CleanSteps Island Cleanup Drive (Victoria)', 'Event Transportation'),
(200.00, '2024-04-20', 'Transportation for CleanSteps Island Cleanup Drive (Comox)', 'Event Transportation'),
(1500.00, '2024-05-30', 'Venue rental and decorations for Conservation Celebration Ball', 'Event Venue'),
(100.00, '2024-05-25', 'Supplies for EcoWarriors! event', 'Event Supplies'),
(2000.00, '2024-04-20', 'Campaign Cost forKeep the Island Green!', 'Campaign Expense'),
(3500.00, '2024-04-20', 'Campaign Cost for Wild Haven!', 'Campaign Expense'),
(2500.00, '2024-03-01', 'Monthly rent for office', 'Office Rent');

INSERT INTO Incurs (expenseID, location, campaignID, employeeID) VALUES
(1, NULL, 1, NULL), -- Expense related to Sow & Grow: Island Tree Planting Rally
(2, NULL, 1, NULL), -- Expense related to CleanSteps Island Cleanup Drive (Victoria)
(3, NULL, 1, NULL), -- Expense related to CleanSteps Island Cleanup Drive (Comox)
(4, NULL, 2, NULL), -- Expense related to Conservation Celebration Ball
(5, NULL, 2, NULL), -- Expense related to EcoWarriors! event
(6, NULL, 1, NULL),
(7, NULL, 2, NULL),
(8, '123 Main St, Victoria, BC', NULL, NULL); -- monthly rent