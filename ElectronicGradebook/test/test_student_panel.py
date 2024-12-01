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
    assert response.json() == {'first_name': 'Johny', 'last_name': 'Bravo', 'username': 'j_bravo', 'date_of_birth': '2024-08-18',
         'class': 'No class assigned', 'role': 'student'}


def test_show_profile_detail_with_class(test_student_with_class):
    response = client.get('student/profile')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'first_name': 'Johny', 'last_name': 'Bravo', 'username': 'j_bravo', 'date_of_birth': '2024-08-18',
         'class': '1A', 'role': 'student'}


def test_reset_password(test_student):
    request_data = {
        'old_password': 'test1234',
        'new_password': 'testtest'
    }
    response = client.put('student/reset-password', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_reset_password_invalid_current_password(test_student):
    request_data = {
        'old_password': 'test',
        'new_password': 'testtest'
    }
    response = client.put('student/reset-password', json=request_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}


def test_show_grades(test_grade):
    response = client.get('student/grades')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'Math': [{'grade': 5, 'date': '2024-09-04', 'added_by': 'Anna Kowalska'}]}


def test_show_grades_not_found(test_student):
    response = client.get('student/grades')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Not found'}


def test_show_attendance(test_attendance):
    response = client.get('student/attendance')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'Math': [{'class_date': '2024-09-04', 'status': 'present', 'added_by': 'Anna Kowalska'}]}


def test_show_attendance_not_found(test_student):
    response = client.get('student/attendance')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Not found'}
