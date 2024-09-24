from datetime import timedelta

from ..main import app
from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt

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


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'student'
    expires_delta = timedelta(days=1)
    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}
