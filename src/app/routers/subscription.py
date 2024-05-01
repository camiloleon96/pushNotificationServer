from typing import Annotated
from models import Subscription, Base
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schemas import SubscriptionBase, SubscriptionResponse
import uuid
from datetime import datetime, timedelta
from pydantic import ValidationError
from routers.user import get_current_user
from worker_task_definition import create_push_notification

router = APIRouter(
    prefix='/subscription',
    tags=['subscription']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def calculate_end_date(start_date):
    end_date = start_date + timedelta(minutes=15)
    return end_date.strftime("%Y-%m-%d %H:%M:%S.%f+00")


@router.post("/", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(subscription: SubscriptionBase, user: user_dependency, db: db_dependency):
    print(user)
    if user is None or user.get('id') != subscription.userId:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    try:
        subscription_id = str(uuid.uuid4())
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f+00")
        end_date = calculate_end_date(datetime.now())
        print(start_date)
        db_subscription = Subscription(
            id=subscription_id,
            userId=subscription.userId,
            planId=subscription.planId,
            paymentMethod=subscription.paymentMethod,
            startDate=start_date,
            endDate=end_date
        )
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)

        new_subscription = SubscriptionResponse(
            id=subscription_id,
            userId=subscription.userId,
            planId=subscription.planId,
            paymentMethod=subscription.paymentMethod,
            startDate=start_date,
            endDate=end_date
        )

        message = "congratulations " + user.get("username") + \
            " you have succesfully activated your new plan: " + subscription_id

        create_push_notification.delay(
            subscription.userId, message)

        return new_subscription

    except ValidationError as e:
        print('[validationError]: '+str(e))
        raise HTTPException(status_code=400, detail="Invalid input")
    except IntegrityError as e:
        print('[IntegrityError]: '+str(e))
        raise HTTPException(
            status_code=400, detail="Input data violates Db constraint")
    except Exception as e:
        print('DefaultException]: '+str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
