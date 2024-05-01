import os
import time

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")


@celery.task(name="create_push_notification")
def create_push_notification(user_name, subscription_id):
    message = "congratulations " + user_name + \
        " you have succesfully activated your new plan " + subscription_id
    print(message)
    return message
