import psycopg2
from psycopg2 import sql
import schedule
import time
from datetime import datetime, timedelta
from worker_task_definition import create_push_notification

# PostgreSQL connection parameters
DB_HOST = "db"
DB_PORT = "5432"
DB_NAME = "dev"
DB_USER = "admin"
DB_PASSWORD = "admin"


def check_subscription_end_dates():
    try:
        print('******check_subscription_end_dates*******')
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        # Define the SQL query to select subscriptions ending within the next 5 minutes
        query = sql.SQL("""
            SELECT id, "userId", "planId", "startDate", "endDate" 
            FROM subscription 
            WHERE "endDate" BETWEEN NOW() AND NOW() + INTERVAL '100 minutes'
        """)

        cursor.execute(query)

        # Fetch all rows
        print("executing query...")
        subscriptions = cursor.fetchall()
        print(subscriptions)

        for subscription in subscriptions:
            id, userId, planId, startDate, endDate = subscription
            print("Subscription ending soon:", planId)
            create_push_notification.delay(
                userId, planId)

        # Close cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        print("Error:", e)


# Schedule the cron job to run every 10 minutes
schedule.every(1).minutes.do(check_subscription_end_dates)

# Run the scheduler loop
while True:
    print('******WHILE*******')
    schedule.run_pending()
    time.sleep(60)
