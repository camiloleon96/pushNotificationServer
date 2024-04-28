from dotenv import load_dotenv
import os
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import App_user
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import uuid
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from schemas import CreateUserRequest, UserResponse, Token

# Load environment variables from the .env file
load_dotenv()

router = APIRouter(
    prefix='/user',
    tags=['user']
)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='user/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(App_user).filter(App_user.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      new_user_data: CreateUserRequest):
    try:
        user_id = str(uuid.uuid4())
        db_new_user = App_user(
            id=user_id,
            email=new_user_data.email,
            username=new_user_data.username,
            password=bcrypt_context.hash(new_user_data.password),
        )

        db.add(db_new_user)
        db.commit()
        db.refresh(db_new_user)

        new_user = UserResponse(
            id=user_id,
            username=new_user_data.username,
            email=new_user_data.email
        )
        return new_user

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


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(
        user.username, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {'access_token': token, 'token_type': 'bearer'}
