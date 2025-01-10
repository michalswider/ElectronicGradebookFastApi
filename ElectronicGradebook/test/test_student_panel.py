from starlette import status
from starlette.testclient import TestClient

from ..main import app
from ..routers.auth import get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_show_profile_detail_without_class(token, test_student):
    response = client.get("student/profile", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "first_name": "Johny",
        "last_name": "Bravo",
        "username": "j_bravo",
        "date_of_birth": "2024-08-18",
        "class": "No class assigned",
        "role": "student",
    }


def test_show_profile_detail_with_class(token, test_student_with_class):
    response = client.get("student/profile", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "first_name": "Johny",
        "last_name": "Bravo",
        "username": "j_bravo",
        "date_of_birth": "2024-08-18",
        "class": "1A",
        "role": "student",
    }


def test_reset_password(token, test_student):
    request_data = {"old_password": "test1234", "new_password": "testtest"}
    response = client.put(
        "student/reset-password",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_reset_password_invalid_current_password(token, test_student):
    request_data = {"old_password": "test", "new_password": "testtest"}
    response = client.put(
        "student/reset-password",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change"}


def test_show_grades(token, test_grade):
    response = client.get("student/grades", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "Math": [{"grade": 5, "date": "2024-09-04", "added_by": "Anna Kowalska"}]
    }


def test_show_grades_not_found(token, test_student):
    response = client.get("student/grades", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}


def test_show_attendance(token, test_attendance):
    response = client.get("student/attendance", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "Math": [
            {
                "class_date": "2024-09-04",
                "status": "present",
                "added_by": "Anna Kowalska",
            }
        ]
    }


def test_show_attendance_not_found(token, test_student):
    response = client.get("student/attendance", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}
