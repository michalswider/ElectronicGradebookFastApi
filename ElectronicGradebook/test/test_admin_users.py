from fastapi.testclient import TestClient
from starlette import status

from ..main import app
from ..routers.auth import get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_add_student(token, test_student):
    request_data = {
        "first_name": "Andrzej",
        "last_name": "Kowalski",
        "username": "a_kowalski",
        "password": "test1234",
        "date_of_birth": "2006-12-06",
        "role": "student",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is None
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.first_name == request_data.get("first_name")
    assert model.last_name == request_data.get("last_name")
    assert model.username == request_data.get("username")
    assert model.date_of_birth.strftime("%Y-%m-%d") == request_data.get("date_of_birth")
    assert model.role == request_data.get("role")


def test_add_student_with_class(token, test_student, test_class):
    request_data = {
        "first_name": "Andrzej",
        "last_name": "Kowalski",
        "username": "a_kowalski",
        "password": "test1234",
        "date_of_birth": "2006-12-06",
        "class_id": 1,
        "role": "student",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is None
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.first_name == request_data.get("first_name")
    assert model.last_name == request_data.get("last_name")
    assert model.username == request_data.get("username")
    assert model.date_of_birth.strftime("%Y-%m-%d") == request_data.get("date_of_birth")
    assert model.class_id == request_data.get("class_id")
    assert model.role == request_data.get("role")


def test_add_teacher_with_subject(token, test_teacher, test_subject):
    request_data = {
        "first_name": "Janina",
        "last_name": "Borkowska",
        "username": "j_borkowska",
        "password": "test1234",
        "date_of_birth": "1987-04-07",
        "subject_id": 1,
        "role": "teacher",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is None


def test_add_user_invalid_role(token):
    request_data = {
        "first_name": "Andrzej",
        "last_name": "Kowalski",
        "username": "a_kowalski",
        "password": "test1234",
        "date_of_birth": "2006-12-06",
        "role": "tchr",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid role: tchr. Allowed roles are 'admin', 'teacher','student'."
    }


def test_add_user_username_exist(token, test_student):
    request_data = {
        "first_name": "Andrzej",
        "last_name": "Kowalski",
        "username": "j_bravo",
        "password": "test1234",
        "date_of_birth": "2006-12-06",
        "role": "student",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username: j_bravo already exist."}


def test_add_student_class_not_exist(token):
    request_data = {
        "first_name": "Marcin",
        "last_name": "Balcerowicz",
        "username": "m_balcerowicz",
        "password": "test1234",
        "date_of_birth": "2002-07-02",
        "class_id": 999,
        "role": "student",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Class with id: 999 does not exist"}


def test_add_teacher_subject_not_exist(token):
    request_data = {
        "first_name": "Jan",
        "last_name": "Kujawa",
        "username": "j_kujawa",
        "password": "test1234",
        "date_of_birth": "1990-03-12",
        "subject_id": 999,
        "role": "teacher",
    }
    response = client.post(
        "admin/add-user", json=request_data, headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Subject with id: 999 does not exist"}


def test_show_all_students(token, test_student):
    response = client.get("admin/students", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    students = response.json()
    assert len(students) > 0
    student_data = next(
        (student for student in students if student["username"] == "j_bravo"), None
    )
    assert student_data is not None
    assert student_data["id"] == 1
    assert student_data["first_name"] == "Johny"
    assert student_data["last_name"] == "Bravo"
    assert student_data["username"] == "j_bravo"
    assert student_data["date_of_birth"] == "2024-08-18"
    assert student_data["role"] == "student"


def test_show_all_teachers(token, test_teacher):
    response = client.get("admin/teachers", headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    teachers = response.json()
    assert len(teachers) > 0
    teacher_data = next(
        (teacher for teacher in teachers if teacher["username"] == "a_kowalska"), None
    )
    assert teacher_data is not None
    assert teacher_data["id"] == 1
    assert teacher_data["first_name"] == "Anna"
    assert teacher_data["last_name"] == "Kowalska"
    assert teacher_data["username"] == "a_kowalska"
    assert teacher_data["role"] == "teacher"


def test_show_student_detail(token, test_student):
    response = client.get(
        "admin/students/?username=j_bravo", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    students = response.json()
    assert students["id"] == 1
    assert students["first_name"] == "Johny"
    assert students["last_name"] == "Bravo"
    assert students["username"] == "j_bravo"
    assert students["date_of_birth"] == "2024-08-18"
    assert students["class"] == "No class assigned"
    assert students["role"] == "student"


def test_show_student_detail_username_not_found(token):
    response = client.get(
        "admin/students/?username=b_bbb", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with username: b_bbb not found"}


def test_show_teacher_detail(token, test_teacher):
    response = client.get(
        "admin/teachers/?username=a_kowalska", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    teachers = response.json()
    assert teachers["id"] == 1
    assert teachers["first_name"] == "Anna"
    assert teachers["last_name"] == "Kowalska"
    assert teachers["username"] == "a_kowalska"
    assert teachers["subject"] == "No subject assigned"
    assert teachers["role"] == "teacher"


def test_show_teacher_detail_username_not_found(token):
    response = client.get(
        "admin/teachers/?username=a_aaa", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with username: a_aaa not found"}


def test_edit_user(token, test_student):
    request_data = {
        "first_name": "Andrzej",
        "last_name": "Kowalski",
        "username": "a_kowalski",
    }
    response = client.put(
        "admin/edit-user/?username=j_bravo",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(User).filter(User.username == "a_kowalski").first()
    assert model.first_name == request_data.get("first_name")
    assert model.last_name == request_data.get("last_name")
    assert model.username == request_data.get("username")


def test_edit_user_username_not_found(token):
    request_data = {
        "first_name": "Andrzej",
        "last_name": "Kowalski",
        "username": "a_kowalski",
    }
    response = client.put(
        "admin/edit-user/?username=testtest",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with username: testtest not found"}


def test_edit_user_username_already_exist(token, test_student, test_teacher):
    request_data = {
        "first_name": "Anastazja",
        "last_name": "Kowalska",
        "username": "a_kowalska",
    }
    response = client.put(
        "admin/edit-user/?username=j_bravo",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username: a_kowalska already exist."}


def test_edit_class_not_exist(token, test_student):
    request_data = {"class_id": 999}
    response = client.put(
        "admin/edit-user/?username=j_bravo",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Class with id: 999 does not exist"}


def test_edit_subject_not_exist(token, test_teacher):
    request_data = {"subject_id": 999}
    response = client.put(
        "admin/edit-user/?username=a_kowalska",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Subject with id: 999 does not exist"}


def test_edit_invalid_role(token, test_student):
    request_data = {"role": "tcher"}
    response = client.put(
        "admin/edit-user/?username=j_bravo",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid role: tcher. Allowed roles are 'admin', 'teacher','student'."
    }


def test_delete_user(token, test_student):
    response = client.delete(
        "admin/delete-user/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert model is None


def test_delete_user_related_grades_error(token, test_grade):
    response = client.delete(
        "admin/delete-user/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "User with id: 1 cannot be deleted because it is associated with table: grades."
    }


def test_delete_user_related_attendance_error(token, test_attendance):
    response = client.delete(
        "admin/delete-user/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "User with id: 1 cannot be deleted because it is associated with table: attendance."
    }


def test_delete_teacher_related_grades_error(token, test_grade):
    response = client.delete(
        "admin/delete-user/2", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "User with id: 2 cannot be deleted because it is associated with table: grades."
    }


def test_delete_teacher_related_attendance_error(token, test_attendance):
    response = client.delete(
        "admin/delete-user/2", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": "User with id: 2 cannot be deleted because it is associated with table: attendance."
    }
