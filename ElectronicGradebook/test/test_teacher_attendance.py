from starlette import status
from starlette.testclient import TestClient

from ..main import app
from ..routers.auth import get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_add_attendance(token, test_attendance):
    request_data = {
        "student_id": 1,
        "subject_id": 1,
        "class_date": "2024-09-11",
        "status": "absent",
    }
    response = client.post(
        "/teacher/add-attendance",
        json=request_data,
        headers=get_authorization_header(token),
    )
    db = TestingSessionLocal()
    model = db.query(Attendance).filter(Attendance.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert model.student_id == request_data.get("student_id")
    assert model.subject_id == request_data.get("subject_id")
    assert model.class_date.strftime("%Y-%m-%d") == request_data.get("class_date")
    assert model.status == request_data.get("status")


def test_add_attendance_user_not_found(token, test_attendance):
    request_data = {
        "student_id": 999,
        "subject_id": 1,
        "class_date": "2024-09-11",
        "status": "absent",
    }
    response = client.post(
        "/teacher/add-attendance",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with id: 999 not found"}


def test_add_attendance_subject_not_exist(token, test_attendance):
    request_data = {
        "student_id": 1,
        "subject_id": 999,
        "class_date": "2024-09-11",
        "status": "absent",
    }
    response = client.post(
        "/teacher/add-attendance",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Subject with id: 999 does not exist"}


def test_add_attendance_invalid_status(token, test_attendance):
    request_data = {
        "student_id": 1,
        "subject_id": 1,
        "class_date": "2024-09-11",
        "status": "abnt",
    }
    response = client.post(
        "/teacher/add-attendance",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid status: abnt. Allowed status are 'present', 'absent', 'excused'."
    }


def test_show_student_attendance(token, test_attendance):
    response = client.get(
        "/teacher/show-student-attendance/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "Math": [
            {
                "id": 1,
                "class_date": "2024-09-04",
                "status": "present",
                "added_by": "Anna " "Kowalska",
            }
        ]
    }


def test_show_student_attendance_user_not_found(token):
    response = client.get(
        "/teacher/show-student-attendance/999", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with id: 999 not found"}


def test_show_student_attendance_student_attendance_not_found(token, test_student):
    response = client.get(
        "/teacher/show-student-attendance/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No attendance records found for student with id: 1"
    }


def test_get_attendance_for_class_on_date(token, test_attendance):
    response = client.get(
        "teacher/attendance/class/1/date?date=2024-09-04",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "1A": {
            "Math": {
                "Johny Bravo": [
                    {
                        "class_date": "2024-09-04",
                        "status": "present",
                        "added_by": "Anna Kowalska",
                    }
                ]
            }
        }
    }


def test_get_attendance_for_class_on_date_class_not_exist(token):
    response = client.get(
        "teacher/attendance/class/999/date?date=2024-09-04",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Class with id: 999 does not exist"}


def test_get_attendance_for_class_on_date_attendance_not_found(
    token, test_student_with_class
):
    response = client.get(
        "teacher/attendance/class/1/date?date=2024-09-04",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No attendance records found for class with id: 1 on date: 2024-09-04"
    }


def test_get_attendance_for_student_in_subject(token, test_attendance):
    response = client.get(
        "teacher/attendance/subject/1/student/1",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "class_date": "2024-09-04",
            "status": "present",
            "added_by": "Anna Kowalska",
        }
    ]


def test_get_attendance_for_student_in_subject_subject_not_exist(token):
    response = client.get(
        "teacher/attendance/subject/999/student/1",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Subject with id: 999 does not exist"}


def test_get_attendance_for_student_in_subject_user_id_not_found(token, test_subject):
    response = client.get(
        "teacher/attendance/subject/1/student/999",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with id: 999 not found"}


def test_get_attendance_for_student_in_subject_attendance_not_found(
    token, test_student, test_subject
):
    response = client.get(
        "teacher/attendance/subject/1/student/1",
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No attendance records found for student with id: 1 in subject with id: 1"
    }


def test_edit_attendance_status(token, test_attendance):
    request_data = {"status": "absent"}
    response = client.put(
        "teacher/edit-attendance/1/1/1",
        json=request_data,
        headers=get_authorization_header(token),
    )
    db = TestingSessionLocal()
    model = db.query(Attendance).filter(Attendance.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.status == request_data.get("status")


def test_edit_attendance_status_subject_not_exist(token, test_attendance):
    request_data = {"status": "absent"}
    response = client.put(
        "teacher/edit-attendance/1/999/1",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Subject with id: 999 does not exist"}


def test_edit_attendance_status_user_id_not_found(token, test_attendance):
    request_data = {"status": "absent"}
    response = client.put(
        "teacher/edit-attendance/999/1/1",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with id: 999 not found"}


def test_edit_attendance_status_attendance_data_not_found(token, test_attendance):
    request_data = {"status": "absent"}
    response = client.put(
        "teacher/edit-attendance/1/2/1",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No attendance data found for attendance_id: 1, subject_id: 2, student_id: 1"
    }


def test_edit_attendance_status_invalid_status(token, test_attendance):
    request_data = {"status": "abst"}
    response = client.put(
        "teacher/edit-attendance/1/1/1",
        json=request_data,
        headers=get_authorization_header(token),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid status: abst. Allowed status are 'present', 'absent', 'excused'."
    }


def test_delete_attendance(token, test_attendance):
    response = client.delete(
        "teacher/delete-attendance/1/1/1", headers=get_authorization_header(token)
    )
    db = TestingSessionLocal()
    model = db.query(Attendance).filter(Attendance.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model is None


def test_delete_attendance_user_id_not_found(token, test_attendance):
    response = client.delete(
        "teacher/delete-attendance/999/1/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User with id: 999 not found"}


def test_delete_attendance_subject_not_exist(token, test_attendance):
    response = client.delete(
        "teacher/delete-attendance/1/999/1", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Subject with id: 999 does not exist"}


def test_delete_attendance_data_not_found(token, test_attendance):
    response = client.delete(
        "teacher/delete-attendance/1/1/999", headers=get_authorization_header(token)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "No attendance data found for attendance_id: 999, subject_id: 1, student_id: 1"
    }
