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
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        query = sql.SQL("""
            SELECT id, "userId", "planId", "startDate", "endDate" 
            FROM subscription 
            WHERE "endDate" BETWEEN NOW() AND NOW() + INTERVAL '10 minutes'
        """)

        cursor.execute(query)

        print("executing query...")
        subscriptions = cursor.fetchall()
        print(subscriptions)

        for subscription in subscriptions:
            id, userId, planId, startDate, endDate = subscription
            print("Subscription ending soon:", planId)
            message = "Subscription ending soon: " + planId
            create_push_notification.delay(
                userId, message)

        cursor.close()
        conn.close()

    except Exception as e:
        print("Error:", e)


schedule.every(1).minutes.do(check_subscription_end_dates)

# Run the scheduler loop
while True:
    print('******WHILE*******')
    schedule.run_pending()
    time.sleep(60)
