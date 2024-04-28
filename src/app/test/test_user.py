from datetime import datetime, timedelta
from unittest.mock import Mock
import pytest
from routers.user import authenticate_user, create_access_token, get_current_user
from fastapi import HTTPException


class MockDB:
    def __init__(self, user=None):
        self.user = user

    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.user


class TestAuthentication:
    def test_successful_authentication(self):
        user = Mock()
        user.username = "test_user"
        user.password = "$2b$12$eICQoU6F9ZkuH4lAe81vluiRKuLK9m030mHLQToHx53uN3tRhKMOO"

        db = MockDB(user=user)

        authenticated_user = authenticate_user("test_user", "goodboy123", db)
        assert authenticated_user == user

    def test_invalid_user_authentication(self):
        db = MockDB(user=None)

        authenticated_user = authenticate_user(
            "nonexistent_user", "password123", db)
        assert authenticated_user == False

    def test_authenticate_user_invalid_password(self):
        user = Mock()
        user.username = "test_user"
        user.password = "$2b$12$eICQoU6F9ZkuH4lAe81vluiRKuLK9m030mHLQToHx53uN3tRhKMOO"

        db = MockDB(user=user)

        authenticated_user = authenticate_user(
            "test_user", "wrong_password", db)
        assert authenticated_user == False


class TestAccessToken:
    def test_create_access_token(self):

        token = create_access_token("test_user", 123, timedelta(minutes=30))
        assert isinstance(token, str)


class TestCurrentUser:
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        # Valid token
        token = create_access_token("test_user", 123, timedelta(minutes=30))
        user = await get_current_user(token)
        assert user == {'username': 'test_user', 'id': 123}

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        # Invalid token
        with pytest.raises(Exception):
            await get_current_user("invalid_token")
