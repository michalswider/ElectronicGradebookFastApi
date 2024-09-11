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
