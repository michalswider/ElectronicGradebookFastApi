from typing import Annotated
from fastapi import Depends
from starlette import status
from starlette.testclient import TestClient
from ..main import app
from .utils import *
from ..routers.auth import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
user_dependency = Annotated[dict, Depends(get_current_user)]

client = TestClient(app)


def test_show_profile_detail_without_class(test_student):
    response = client.get('student/profile')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'first_name': 'Johny', 'last_name': 'Bravo', 'username': 'j_bravo', 'date_of_birth': '2024-08-18',
         'class': 'No class assigned', 'role': 'student'}]


def test_show_profile_detail_with_class(test_student_with_class):
    response = client.get('student/profile')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'first_name': 'Johny', 'last_name': 'Bravo', 'username': 'j_bravo', 'date_of_birth': '2024-08-18',
         'class': '1A', 'role': 'student'}]
