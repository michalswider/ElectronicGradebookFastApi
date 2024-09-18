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


def test_add_grade(test_grade):
    request_data = {
        'student_id': 1,
        'subject_id': 1,
        'grade': 2,
        'date': '2024-09-18'
    }
    response = client.post('teacher/grades/add-grade', json=request_data)
    db = TestingSessionLocal()
    model = db.query(Grade).filter(Grade.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Grade added successfully"}
    assert model is not None
    assert model.student_id == request_data.get('student_id')
    assert model.subject_id == request_data.get('subject_id')
    assert model.grade == request_data.get('grade')
    assert model.date.strftime("%Y-%m-%d") == request_data.get('date')


def test_add_grade_user_id_not_found(test_grade):
    request_data = {
        'student_id': 999,
        'subject_id': 1,
        'grade': 2,
        'date': '2024-09-18'
    }
    response = client.post('teacher/grades/add-grade', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}


def test_add_grade_subject_not_exist(test_student):
    request_data = {
        'student_id': 1,
        'subject_id': 999,
        'grade': 2,
        'date': '2024-09-18'
    }
    response = client.post('teacher/grades/add-grade', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_show_student_grades(test_grade):
    response = client.get('teacher/grades/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'Math': [{'id': 1, 'grade': 5, 'date': '2024-09-04', 'added_by': 'Anna Kowalska'}]}