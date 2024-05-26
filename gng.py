#!/usr/bin/env python3
import psycopg2
import time

def connect():
    try: 
        conn = psycopg2.connect(host = 'studentdb.csc.uvic.ca', user='c370_s156', password = '67TYfAGX')
        return conn
    except psycopg2.Error as err:
        print("Unable to connect to the database")
        print(err)
        return None
    
QUERIES = {
        "Q1": ("How much was fundraised per campaign?"),
        "Q2": ("Which campaigns have a larger campaign cost than average?"),
        "Q3": ("Which donors have contributed to campaigns and also supported events but are not volunteers?"),
        "Q4": ("Group campaigns and events by the employee that managed them"),
        "Q5": ("Which donor has contributed the most?"),
        "Q6": ("How many volunteers participated in each campaign?"),
        "Q7": ("Which events were fundraisers?"),
        "Q8": ("What is the expense breakdown?"),
        "Q9": ("How long is each campaign?"),
        "Q10": ("Which volunteers have participated the most?"),
        "Q11": ("Which donors have contributed to multiple campaigns?"),
        "Q12": ("What is the total cost of each campaign?")
    }
    
def query_output(query):
    dbconn = connect()
    if dbconn:
        try:
            cursor = dbconn.cursor()
            print("Results for Query {}: {}".format(query, QUERIES[query]))
            cursor.execute("SELECT * FROM {}".format(query))
            for row in cursor.fetchall():
                print(f"{row[0]}, {row[1]:,.2f}")

        except (Exception, psycopg2.Error) as err:
            print("Error while executing query:", err)

    #Close connection
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()
    
    #Pause before returning to main menu
    time.sleep(2)

def add_volunteer(campaign_id):

    new_existing_volunteer = input("Would you like to add a new volunteer (n) or an existing volunteer (e)?")
    
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        if new_existing_volunteer == "e":
            cursor.execute("SELECT * FROM Volunteers")
            volunteers = cursor.fetchall()

            if volunteers:
                print("Existing Volunteers: ")

                for volunteer in volunteers:
                    print(f"ID: {volunteer[0]}, Name: {volunteer[1]}, Contact: {volunteer[4]}")
                    time.sleep(0.3)

                volunteer_id = input("Enter the ID of the volunteer you want to add to the campaign: ")
                cursor.execute("INSERT INTO ParticipatesIn (volunteerID, campaignID) VALUES (%s, %s)", (volunteer_id, campaign_id))
                dbconn.commit()
                print("Volunteer added to the campaign successfully!")

        elif new_existing_volunteer == "n":
            volunteer_name = input("Enter volunteer name: ")
            volunteer_contact = input("Enter volunteer contact info: ")
            cursor.execute("INSERT INTO Volunteers (name, numParticipatedIn, contactInfo) VALUES (%s, %s, %s)", (volunteer_name, 0, volunteer_contact))
            dbconn.commit()
            print("New volunteer added successfully.")

    except (Exception, psycopg2.Error) as error:
        print("Error while adding volunteer:", error)
        dbconn.rollback()
        return

    # Closing database connection.
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()    

def schedule_volunteers(event_id):
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        # Get the campaign ID for the specified event
        cursor.execute("""
                        SELECT campaign FROM Holds WHERE event = %s
                        """, (event_id,))
        campaign_id = cursor.fetchone()[0]

        # Get the names of volunteers participating in the same campaign
        cursor.execute("""
                        SELECT *
                        FROM Volunteers
                        JOIN ParticipatesIn ON Volunteers.volunteerID = ParticipatesIn.volunteerID
                        WHERE ParticipatesIn.campaignID = %s
                        AND NOT EXISTS (
                            SELECT 1
                            FROM ScheduledFor
                            WHERE ScheduledFor.volunteerID = ParticipatesIn.volunteerID
                            AND ScheduledFor.eventID = %s
                        )
                        """, (campaign_id, event_id))
        volunteers = cursor.fetchall()

        if volunteers:
            print("Volunteers available:")
            for volunteer in volunteers:
                print(f"Name: {volunteer[1]} (ID: {volunteer[0]}), Tier: {volunteer[3]} (Participated in {volunteer[2]} Campaigns)")
        else:
            print("No availabel volunteers.")
            return

        scheduled_volunteer = input("Input the ID of the volunteer you wish to schedule to this event: ")

        cursor.execute("""
                            INSERT INTO ScheduledFor (volunteerID, eventID)
                            VALUES (%s, %s)
                            """, (scheduled_volunteer, event_id))
        
        dbconn.commit()
        print("Volunteers scheduled successfully for the event.")


    except (Exception, psycopg2.Error) as error:
        print("Error occurred while scheduling volunteers: ", error)
        dbconn.rollback()

    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def add_event(campaign_id):
    event_name = input("Enter event name: ")
    event_location = input("Enter event location: ")
    event_description = input("Enter event description: ")
    event_time = input("Enter event date and time (YYYY-MM-DD HH:MM:SS): ")

    try:
        dbconn = connect()
        cursor = dbconn.cursor()
        
        # Insert new event
        cursor.execute("INSERT INTO Events (name, location, description, eventTime, fundraisedAmount) VALUES (%s, %s, %s, %s, 0) RETURNING eventID", (event_name, event_location, event_description, event_time))
        event_id = cursor.fetchone()[0]  # Fetch the generated eventID
        dbconn.commit()

        # Link event to campaign
        cursor.execute("INSERT INTO Holds (campaign, event) VALUES (%s, %s)", (campaign_id, event_id))
        dbconn.commit()

        print("Event scheduled successfully.")

        schedule = input("Would you like to schedule volunteers for this event? (y/n)")

        if schedule == 'y':
            schedule_volunteers(event_id)
        elif schedule == 'n':
            return
        else:
            print("Invalid input. please enter valid option")

    except (Exception, psycopg2.Error) as error:
        print("Error while scheduling event:", error)
        dbconn.rollback()

    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def campaign_state(campaign_id):
    try:
        dbconn = connect()
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM Campaigns WHERE campaignID = %s", (campaign_id,))
        campaign = cursor.fetchone()
        if campaign:
            print("Campaign ID:", campaign[0])
            print("Name:", campaign[2])
            print("Description:", campaign[3])
            print("Cost:", campaign[1])
            print("Start Date:", campaign[4])
            print("End Date:", campaign[5])

            cursor.execute("""
                SELECT * FROM Volunteers
                JOIN ParticipatesIn ON Volunteers.volunteerID = ParticipatesIn.volunteerID
                WHERE ParticipatesIn.campaignID = %s
            """, (campaign_id,))
            volunteers = cursor.fetchall()

            if volunteers:
                print("Volunteers for this campaign: ")
                for volunteer in volunteers:
                    print("- Name:", volunteer[1])
                    print("  Contact Info:", volunteer[4])
                    

            cursor.execute("""
                SELECT Events.name, Events.location, Events.eventTime
                FROM Events
                JOIN Holds ON Events.eventID = Holds.event
                WHERE Holds.campaign = %s
            """, (campaign_id,))
            events = cursor.fetchall()

            if events:
                print("Events:")
                for event in events:
                    print("- Name:", event[0])
                    print("  Location:", event[1])
                    print("  Time:", event[2])
        else:
            print("Campaign not found.")

    except psycopg2.Error as err:
        print("Error occurred:", err)

    #Close connection
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()

def query_menu():
    print("Choose from the list of queries available, or press 'b' to go back:")

    for query, description in QUERIES.items():
            print(f"{query}: {description}")
            time.sleep(0.3)

    choice = input("Enter your choice: ")
    
    if choice == 'b':
        print("Returning to previous menu... ")
        return
    
    elif choice.upper() not in QUERIES.keys():
        print("Invalid choice. Please enter a valid query")

    else:
        query_output(choice.upper())
        print("Query executed, returning to previous menu... ")

def setup_campaign():

    #Collect relative info for campaign
    campaign_name = input("Enter campaign name: ")
    campaign_cost = float(input("Enter campaign cost: "))
    campaign_description = input("Enter campaign description: ")
    start_date = input("Enter campaign start date (YYYY-MM-DD): ")
    end_date = input("Enter campaign end date (YYYY-MM-DD): ")

    try:
        dbconn = connect()
        cursor = dbconn.cursor()
        cursor.execute("""
            INSERT INTO Campaigns(cost, name, description, startDate, endDate) VALUES
            (%s, %s, %s, %s, %s) RETURNING campaignID
            """, (campaign_cost, campaign_name, campaign_description, start_date, end_date))
        campaign_id = cursor.fetchone()[0]  # Fetch the generated campaignID

        dbconn.commit()
        print("Campaign created successfully! Campaign ID:", campaign_id)

        add_a_campaign_expense(campaign_cost, campaign_id)

    except (Exception, psycopg2.Error) as err:
        print("Error while setting up campaign:", err)
        dbconn.rollback()
        return
    
    print("Campaign state (c): ")
    campaign_state(campaign_id)

    #Close connection
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()

    while True:
        volunteer = input("Would you like to add a volunteer to this campaign or check the current campaign state? (y/n/c): ")
        if volunteer == "y":
            add_volunteer(campaign_id)
        elif volunteer == "c":
            campaign_state(campaign_id)
        elif volunteer == "n":
            break
        else:
            print("Invalid choice. please enter a valid input")

    while True:
        event = input("Would you like to schedule an event for this campaign or check the currect campaign state? (y/n/c): ")
        if event == 'y':
            add_event(campaign_id)
        elif event == 'c':
            campaign_state(campaign_id)
        else:
            break

def fund_reporting():
    #Get fund info from database
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        cursor.execute("SELECT campaign, SUM(amount) FROM Funds GROUP BY campaign")
        inflows = cursor.fetchall()

        cursor.execute("SELECT Incurs.campaignID, SUM(Expenses.amount) FROM Expenses JOIN Incurs ON Expenses.expenseID = Incurs.expenseID GROUP BY Incurs.campaignID;")
        outflows = cursor.fetchall()

    except psycopg2.Error as e:
        print("Error occurred while fetching data:", e)
        return
    
    inflow_dict = dict(inflows)
    outflow_dict = dict(outflows)
    scale = 1000
    text_or_ascii = input("press 't' for a textual report on data, 'a' for an ASCII Bar Chart, or 'b' to go back to the [revious menu]")

    if text_or_ascii == 't':
        print("Fund Inflows and Outflows Textual Report:")
        print("Campaign ID  |  Fund Inflows  |  Fund Outflows  |  Net Balance")
        for campaign_id in inflow_dict.keys():
            inflow = inflow_dict.get(campaign_id, 0)
            outflow = outflow_dict.get(campaign_id, 0)
            net_balance = str(inflow - outflow)
            if float(net_balance) < 0:
                net_balance += " (Negative)"
            print(f"{campaign_id:<12} |  {inflow:<14} |  {outflow:<15} |  {net_balance}")


        back = input("\n\n press any key to return to previous menu")
        if back:
            if cursor:
                cursor.close()
            if dbconn:
                dbconn.close()
            return

    elif text_or_ascii == 'a':
        print("\nASCII Bar Chart (Inflows and Outflows):")
        for campaign_id in inflow_dict.keys():
            inflow = inflow_dict.get(campaign_id, 0)
            outflow = outflow_dict.get(campaign_id, 0)
            net_balance = str(inflow - outflow)
            inflow_bar = '#' * int((inflow / scale))
            outflow_bar = '#' * int((outflow / scale))
            net_balance_bar = '#' * int((float(net_balance) / scale))
            if float(net_balance) < 0:
                net_balance += " (Negative)"
            print(f"Campaign {campaign_id}:")
            print(f"Inflows:   {inflow_bar} {inflow}")
            print(f"Outflows:  {outflow_bar} {outflow}")
            print(f"Net Balance:   {net_balance_bar} {net_balance}")
            print()
        
        back = input("\n\n press any key to return to previous menu")
        if back:
            if cursor:
                cursor.close()
            if dbconn:
                dbconn.close()
            return

    elif text_or_ascii == 'b':
        print("Returning to previous menu... ")
        if cursor:
                cursor.close()
        if dbconn:
            dbconn.close()
        return
    else:
        print("Invaid input. Please input a valid entry")

#TODO: Add Members to this functionality
def member_history():
    member_id_or_name = input("Enter member name or ID: ")
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        if member_id_or_name.isdigit():
            member_id_or_name = int(member_id_or_name)
            cursor.execute("""
                            SELECT Volunteers.name, Campaigns.name, Campaigns.campaignID 
                            FROM Campaigns 
                            JOIN ParticipatesIn ON Campaigns.campaignID = ParticipatesIn.campaignID
                            JOIN Volunteers ON Volunteers.volunteerID = ParticipatesIn.volunteerID 
                            WHERE ParticipatesIn.volunteerID = %s
                            """, (member_id_or_name,))
        else:
            cursor.execute("""
                            SELECT Volunteers.name, Campaigns.name, Campaigns.campaignID 
                            FROM Campaigns 
                            JOIN ParticipatesIn ON Campaigns.campaignID = ParticipatesIn.campaignID 
                            JOIN Volunteers ON Volunteers.volunteerID = ParticipatesIn.volunteerID 
                            WHERE Volunteers.name = %s
                            """, (member_id_or_name,))
            
        campaigns = cursor.fetchall()

        if campaigns:
            print(f"Campaigns worked on by Member {member_id_or_name}:")
            for campaign in campaigns:
                print(f"Member Name: {campaign[0]}, Campaign Name: {campaign[1]}, Campaign ID: {campaign[2]}")
        else:
            print("No campaign history found for Member", member_id_or_name)

    except psycopg2.Error as e:
        print("Error occurred while fetching campaign history:", e)

    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()

def campaign_history():
    campaign_id = input("Enter campaign id: ")
    try:
        dbconn = connect()
        cursor = dbconn.cursor()
        cursor.execute("""
                       SELECT Volunteers.name, Volunteers.volunteerID FROM 
                       Volunteers JOIN ParticipatesIn ON Volunteers.volunteerID = ParticipatesIn.volunteerID
                       WHERE ParticipatesIn.campaignID = %s
                       """, (campaign_id,))
        members = cursor.fetchall()

        if members:
            print(f"Members who participated in Campaign {campaign_id}:")
            for member in members:
                print(f"Name: {member[0]}, ID: {member[1]}")
            
        else:
            print(f"No members found for Campaign {campaign_id}")

    except psycopg2.Error as e:
        print ("Error occured while fetching members: ", e)
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()

def history_menu():
    choice = input("Press 1 if you'd like to see the history of which members participated in a specific campaign, or press 2 if you'd like to look up a specific member's history: ")

    if choice == '1':
        campaign_history()
    elif choice == '2':
        member_history()
    else:
        print("Invalid choice. Please enter a valid option")

#TODO: Add annotations to campaigns, member records, or any other piece of data you believe appropriate.
def current_campaigns():
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        # Get all ongoing campaigns
        cursor.execute("""
                        SELECT *
                        FROM Campaigns
                        WHERE startDate <= CURRENT_DATE AND endDate >= CURRENT_DATE
                        """)
        ongoing_campaigns = cursor.fetchall()

        if not ongoing_campaigns:
            print("No ongoing campaigns at the moment.")
            if cursor:
                cursor.close()
            if dbconn:
                dbconn.close()
            return

        # Display ongoing campaigns and their future events
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        print(f"Current Campaigns on {current_date}")
        for campaign in ongoing_campaigns:
            campaign_id = campaign[0]
            campaign_name = campaign[2]
            print(f"\nCampaign: {campaign_name} (ID: {campaign_id})")
            
            # Get future events for the campaign
            cursor.execute("""
                            SELECT *
                            FROM Events
                            JOIN Holds ON Events.eventID = Holds.event
                            WHERE campaign = %s AND Events.eventTime >= CURRENT_TIMESTAMP
                            ORDER BY Events.eventTime
                            """, (campaign_id,))
            future_events = cursor.fetchall()

            if future_events:
                print("Future Events:")
                for event in future_events:
                    event_id = event[0]
                    event_location = event[2]
                    event_name = event[1]
                    event_start_date = event[4].strftime('%Y-%m-%d')
                    print(f"Event: {event_name} (ID: {event_id}), Location: {event_location}, Start Date: {event_start_date}")
            else:
                print("No future events scheduled for this campaign.")

    except psycopg2.Error as e:
        print("Error occurred while fetching ongoing campaigns and events:", e)
    
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()

def donor_history(donor_id):
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        cursor.execute("""
                        SELECT f.amount, f.depositDate, c.name AS campaign_name
                        FROM Funds f
                        JOIN Campaigns c ON f.campaign = c.campaignID
                        WHERE f.donor = %s
                        ORDER BY f.depositDate DESC
                        """, (donor_id,))
        
        donor_history = cursor.fetchall()
        if donor_history:
            print("\nDonation History for Donor ID:", donor_id)
            for donation in donor_history:
                print("Amount:", donation[0])
                print("Deposit Date:", donation[1])
                print("Campaign:", donation[2])
                print("---------------------")
        else:
            print("No donation history found for Donor ID:", donor_id)

    except psycopg2.Error as e:
        print("Error occurred while fetching donor history:", e)
    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def donor_info():
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        cursor.execute("""
                        SELECT donorID, name, tier
                        FROM Donors
                        """)
        
        donors = cursor.fetchall()
        if donors:
            print("List of Donors:")
            for donor in donors:
                print(f"Name: {donor[1]} (ID: {donor[0]}), Tier: {donor[2]}")
        else:
            print("No donors found.")
            return
        chosen_donor = input("Input the id of the donor you'd like to see donation amounts for: ")

        donor_history(chosen_donor)
        
    except psycopg2.Error as e:
        print("Error occurred while fetching donors:", e)
    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def delete_campaign(campaign_id):
    
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        # Check if the campaign ID exists in the Campaigns table
        cursor.execute("SELECT * FROM Campaigns WHERE campaignID = %s", (campaign_id,))
        campaign = cursor.fetchone()

        if campaign:
            # Delete related data in other tables first
            cursor.execute("DELETE FROM Holds WHERE campaign = %s", (campaign_id,))
            cursor.execute("DELETE FROM Funds WHERE campaign = %s", (campaign_id,))
            cursor.execute("DELETE FROM ParticipatesIn WHERE campaignID = %s", (campaign_id,))
            cursor.execute("DELETE FROM Updates WHERE campaignID = %s", (campaign_id,))
            cursor.execute("DELETE FROM Manages WHERE campaignID = %s", (campaign_id,))
            cursor.execute("DELETE FROM Incurs WHERE campaignID = %s", (campaign_id,))

            # Now delete the campaign itself
            cursor.execute("DELETE FROM Campaigns WHERE campaignID = %s", (campaign_id,))
            dbconn.commit()
            print("Campaign successfully deleted.")
        else:
            print("Campaign ID not found.")

    except psycopg2.Error as e:
        print("Error occurred while deleting campaign:", e)

    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def add_a_campaign_expense(amount, campaign_id):
    # Prompt user for expense date
    expense_date = input("Enter the expense date (YYYY-MM-DD) (press 't' for today): ")
    if expense_date == 't':
        expense_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))  # Get today's date

    # Prompt user for expense purpose and type
    purpose = input("Enter a brief description of the expense purpose: ")
    expense_type = input("Enter the expense type: ")

    try:
        # Connect to the database
        dbconn = connect()
        cursor = dbconn.cursor()

        # Insert expense into Expenses table
        cursor.execute("""
                        INSERT INTO Expenses (amount, expenseDate, purpose, expenseType)
                        VALUES (%s, %s, %s, %s)
                        RETURNING expenseID
                        """, (amount, expense_date, purpose, expense_type))

        # Fetch the generated expense ID
        expense_id = cursor.fetchone()[0]

        # Insert expense details into Incurs table
        cursor.execute("""
                        INSERT INTO Incurs (expenseID, location, campaignID, employeeID)
                        VALUES (%s, NULL, %s, NULL)
                        """, (expense_id, campaign_id))

        # Commit the transaction
        dbconn.commit()
        print("Expense added successfully!")

    except psycopg2.Error as e:
        print("Error occurred while adding expense:", e)

    finally:
        # Close cursor and database connection
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def add_a_donation():
    campaign_id = input("Enter the ID of the campaign the donation is for: ")
    donor_id = input("Enter the ID of the donor: ")
    amount = input("Enter the donation amount: ")
    deposit_date = input("Enter the deposit date (YYYY-MM-DD): ")
    payment_method = input("Enter the payment method: ")

    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        cursor.execute("""
                        INSERT INTO Funds (campaign, donor, amount, depositDate, paymentMethod)
                        VALUES (%s, %s, %s, %s, %s)
                        """, (campaign_id, donor_id, amount, deposit_date, payment_method))
        
        dbconn.commit()
        print("Donation added successfully!")

    except psycopg2.Error as e:
        print("Error occurred while adding donation:", e)
    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def expense_breakdown():
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        cursor.execute("""
                        SELECT expenseType, SUM(amount)
                        FROM Expenses
                        GROUP BY expenseType
                        """)
        expenses = cursor.fetchall()

        if expenses:
            print("Expense Breakdown by Category:")
            for category, amount in expenses:
                print(f"{category}: {amount:,.2f}")
        else:
            print("No expense data available.")

    except psycopg2.Error as e:
        print("Error occurred while fetching expense breakdown:", e)
    
    if cursor:
        cursor.close()
    if dbconn:
        dbconn.close()
 
def past_campaigns():
    try:
        dbconn = connect()
        cursor = dbconn.cursor()

        # Get all past campaigns
        cursor.execute("""
                        SELECT *
                        FROM Campaigns
                        WHERE endDate < CURRENT_DATE
                        """)
        past_campaigns = cursor.fetchall()

        if not past_campaigns:
            print("No past campaigns.")
            return

        print("Past Campaigns:")
        for campaign in past_campaigns:
            campaign_id = campaign[0]
            campaign_name = campaign[2]
            print(f"\nCampaign: {campaign_name} (ID: {campaign_id})")

            # Get past events for the campaign
            cursor.execute("""
                            SELECT *
                            FROM Events
                            JOIN Holds ON Events.eventID = Holds.event
                            WHERE campaign = %s AND Events.eventTime < CURRENT_TIMESTAMP
                            ORDER BY Events.eventTime
                            """, (campaign_id,))
            past_events = cursor.fetchall()

            if past_events:
                print("Past Events:")
                for event in past_events:
                    event_id = event[0]
                    event_location = event[2]
                    event_name = event[1]
                    event_start_date = event[4].strftime('%Y-%m-%d')
                    print(f"Event: {event_name} (ID: {event_id}), Location: {event_location}, Start Date: {event_start_date}")
            else:
                print("No past events for this campaign.")

    except psycopg2.Error as e:
        print("Error occurred while fetching past campaigns and events:", e)

    finally:
        if cursor:
            cursor.close()
        if dbconn:
            dbconn.close()

def main():
    
    while True:
        print("""
                        |
                    \       /
                      .-"-.
                 --  /     \  --
`~~^~^~^~^~^~^~^~^~^-=======-~^~^~^~~^~^~^~^~^~^~^~`
`~^_~^~^~-~^_~^~^_~-=========- -~^~^~^-~^~^_~^~^~^~`
`~^~-~~^~^~-^~^_~^~~ -=====- ~^~^~-~^~_~^~^~~^~-~^~`
`~^~^~-~^~~^~-~^~~-~^~^~-~^~~^-~^~^~^-~^~^~^~^~~^~-`
                  jgs
              

            ██████╗ ███╗   ██╗ ██████╗ 
            ██╔════╝ ████╗  ██║██╔════╝ 
            ██║  ███╗██╔██╗ ██║██║  ███╗
            ██║   ██║██║╚██╗██║██║   ██║
            ╚██████╔╝██║ ╚████║╚██████╔╝
            ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
                                        
              """)
        print("\n Welcome to the Green-not-Greed (GnG) Database!")

        print(" 1: Execute a query")
        print(" 2: Setup a campaign")
        print(" 3: Fund Reporting")
        print(" 4: Browse Membership History")
        print(" 5: See Ongoing Campaigns and their events")
        print(" 6: Add an event to an existing campaign")
        print(" 7: Check the state of a campaign")
        print(" 8: Expesne Breakdown")
        print(" 9: Get Donor Info")
        print(" 10: Schedule a volunteer")
        print(" 11: Add a volunteer")
        print(" 12: Add a Campaign Expense")
        print(" 13: Delete Campaign")
        print(" 14: View Past Campaigns")
        print(" q: Quit\n")

        choice = input("Enter your choice: ")

        if choice == 'q':
            print("Exiting program...")
            break

        if choice == '1':
            query_menu()
        elif choice == '2':
            setup_campaign()
        elif choice == '3':
            fund_reporting()
        elif choice == '4':
            history_menu()
        elif choice == '5':
            current_campaigns()
        elif choice == '6':
            campaign = input("Enter the campaign's id: ")
            add_event(campaign)
        elif choice == '7':
            campaign = input("Enter the campaign's id: ")
            campaign_state(campaign)
        elif choice == '8':
            expense_breakdown()
        elif choice == '9':
            donor_info()
        elif choice == '10':
            event = input("Enter the event's id: ")
            schedule_volunteers(event)
        elif choice == '11':
            campaign = input("Enter the campaign's id: ")
            add_volunteer(campaign)
        elif choice == '12':
            campaign = input("Enter the campaign's id: ")
            amount = input("Enter the expense amount: ")
            add_a_campaign_expense(amount, campaign)
        elif choice == '13':
            campaign = input("Enter the campaign's id: ")
            delete_campaign(campaign)
        elif choice == '14':
            past_campaigns()
        else:
            print("Invalid choice. Please enter a valid option")

        time.sleep(1)


if __name__ == "__main__": main()
