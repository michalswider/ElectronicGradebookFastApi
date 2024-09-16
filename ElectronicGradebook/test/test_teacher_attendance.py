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


def test_add_attendance(test_attendance):
    request_data = {
        'student_id': 1,
        'subject_id': 1,
        'class_date': '2024-09-11',
        'status': 'absent'
    }
    response = client.post('/teacher/add-attendance', json=request_data)
    db = TestingSessionLocal()
    model = db.query(Attendance).filter(Attendance.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert model.student_id == request_data.get('student_id')
    assert model.subject_id == request_data.get('subject_id')
    assert model.class_date.strftime("%Y-%m-%d") == request_data.get('class_date')
    assert model.status == request_data.get('status')


def test_add_attendance_user_not_found(test_attendance):
    request_data = {
        'student_id': 999,
        'subject_id': 1,
        'class_date': '2024-09-11',
        'status': 'absent'
    }
    response = client.post('/teacher/add-attendance', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}


def test_add_attendance_subject_not_exist(test_attendance):
    request_data = {
        'student_id': 1,
        'subject_id': 999,
        'class_date': '2024-09-11',
        'status': 'absent'
    }
    response = client.post('/teacher/add-attendance', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_add_attendance_invalid_status(test_attendance):
    request_data = {
        'student_id': 1,
        'subject_id': 1,
        'class_date': '2024-09-11',
        'status': 'abnt'
    }
    response = client.post('/teacher/add-attendance', json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Invalid status: abnt. Allowed status are 'present', 'absent', 'excused'."}


def test_show_student_attendance(test_attendance):
    response = client.get('/teacher/show-student-attendance/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'Math': [{'id': 1, 'class_date': '2024-09-04', 'status': 'present', 'added_by': 'Anna '
                                                                                                               'Kowalska'}]}


def test_show_student_attendance_user_not_found():
    response = client.get('/teacher/show-student-attendance/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}


def test_show_student_attendance_student_attendance_not_found(test_student):
    response = client.get('/teacher/show-student-attendance/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No attendance records found for student with id: 1'}


def test_get_attendance_for_class_on_date(test_attendance):
    response = client.get('teacher/attendance/class/1/date?date=2024-09-04')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'1A': {
        'Math': {'Johny Bravo': [{'class_date': '2024-09-04', 'status': 'present', 'added_by': 'Anna Kowalska'}]}}}


def test_get_attendance_for_class_on_date_class_not_exist():
    response = client.get('teacher/attendance/class/999/date?date=2024-09-04')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Class with id: 999 does not exist'}


def test_get_attendance_for_class_on_date_attendance_not_found(test_student_with_class):
    response = client.get('teacher/attendance/class/1/date?date=2024-09-04')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No attendance records found for class with id: 1 on date: 2024-09-04'}


def test_get_attendance_for_student_in_subject(test_attendance):
    response = client.get('teacher/attendance/subject/1/student/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'class_date': '2024-09-04', 'status': 'present', 'added_by': 'Anna Kowalska'}]


def test_get_attendance_for_student_in_subject_subject_not_exist():
    response = client.get('teacher/attendance/subject/999/student/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}
