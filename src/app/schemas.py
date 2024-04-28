from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "milo",
                    "email": "milo@gmail.com",
                    "password": "goodboy123",
                }
            ]
        }
    }


class UserResponse(BaseModel):
    id: str
    username: str
    email: str


class SubscriptionBase(BaseModel):
    userId: str
    planId: str
    paymentMethod: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "userId": "Milo123",
                    "planId": "plusPlan",
                    "paymentMethod": "card",
                }
            ]
        }
    }


class SubscriptionResponse(SubscriptionBase):
    id: str
    startDate: str
    endDate: str
