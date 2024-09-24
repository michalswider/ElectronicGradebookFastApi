from typing import Annotated
from fastapi import Depends
from ..main import app
from .utils import *
from ..routers.auth import get_db, authenticate_user

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_student):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_student.username, 'test1234', db)
    assert authenticated_user is not False
    assert authenticated_user.username == test_student.username


def test_authenticate_user_wrong_username():
    db = TestingSessionLocal()
    authenticated_user = authenticate_user("wrong_username", 'test1234', db)
    assert authenticated_user is False


def test_authenticate_user_wrong_password(test_student):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_student.username, 'wrong_password', db)
    assert authenticated_user is False
