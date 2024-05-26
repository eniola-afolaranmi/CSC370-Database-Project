-- Q1:How much was fundraised per campaign?
CREATE VIEW Q1 AS
    SELECT Campaigns.name AS campaignName, SUM(Events.fundraisedAmount) AS totalFundraised
    FROM Campaigns
    JOIN Holds on campaignID = campaign
    JOIN Events on event = eventID
    GROUP BY Campaigns.name;

-- Q2: Which campaigns have a larger campaign cost than average
CREATE VIEW Q2 AS
    SELECT Campaigns.name AS campaignName, cost AS expensiveCampaigns
        FROM Campaigns
            WHERE cost > (SELECT AVG(cost) FROM Campaigns); 

-- Q3: Which donors have contributed to campaigns and also supported events but are not volunteers?
CREATE VIEW Q3 AS 
SELECT name
    FROM Donors
        WHERE donorID in (SELECT donor FROM Funds) INTERSECT 
            SELECT name FROM Members;

-- Q4: Group campaigns and events by the employee that managed them
CREATE VIEW Q4 AS
SELECT Employees.name AS employee_name, Campaigns.name AS campaignName, Events.name AS eventName
    FROM Events
    JOIN Holds ON Events.eventID = Holds.event
    JOIN Campaigns  ON Holds.campaign = Campaigns.campaignID
    JOIN Manages ON Campaigns.campaignID = Manages.campaignID
    JOIN Employees ON Manages.employeeID = Employees.employeeID;

-- Q5: Which donor has contributed the most?
CREATE VIEW Q5 AS
SELECT name, (SELECT SUM(amount) FROM Funds WHERE donor = Donors.donorID ) AS totalDonated
    FROM Donors
    WHERE ( SELECT SUM(amount) FROM Funds WHERE donor = Donors.donorID) >= ALL (SELECT SUM(amount) FROM Funds GROUP BY donor);

-- Q6: How many volunteers participated in each campaign?
CREATE VIEW Q6 AS
SELECT Campaigns.name AS campaignName, COUNT(*) AS volunteerCount
FROM ParticipatesIn
JOIN Campaigns ON Campaigns.campaignID = ParticipatesIn.campaignID
GROUP BY Campaigns.name, ParticipatesIn.campaignID;

-- Q7: Which events were fundraisers?
CREATE VIEW Q7 AS
SELECT name AS eventName, fundraisedAmount
    FROM Events
        WHERE fundraisedAmount > 0;

-- Q8: What is the expense breakdown?
CREATE VIEW Q8 AS
SELECT expenseType, SUM(amount) AS totalExpenses
    FROM Expenses
    GROUP BY expenseType
    ORDER BY totalExpenses DESC ;

-- Q9: How long is each campaign?
CREATE VIEW Q9 AS
SELECT name AS campaignName, EXTRACT(DAY FROM (endDate - startDate)) AS campaignDuration
FROM Campaigns;


-- Q10: Which volunteers have participated the most?
CREATE VIEW Q10 AS
SELECT name AS volunteerName, numParticipatedIn AS numCampaignsParticipatedIn
FROM Volunteers
ORDER BY numParticipatedIn DESC;

-- Q11: Which donors have contributed to multiple campaigns?
CREATE VIEW Q11 AS
SELECT Donors.name as donorName, Campaigns.name AS donatedCampaigns
FROM Donors 
JOIN Funds f1 on Donors.donorID = f1.donor
JOIN Funds f2 ON f1.donor = f2.donor AND f1.campaign <> f2.campaign
JOIN Campaigns on f1.campaign = Campaigns.campaignID
GROUP BY Donors.name, Campaigns.name;

-- Q12: What is the total cost of each campaign
CREATE VIEW Q12  AS
SELECT Campaigns.name as campaignName, SUM(Expenses.amount) as totalCost
FROM Campaigns
JOIN Incurs ON Campaigns.campaignID = Incurs.campaignID
JOIN Expenses ON Incurs.expenseID = Expenses.expenseID
GROUP BY Campaigns.name;

