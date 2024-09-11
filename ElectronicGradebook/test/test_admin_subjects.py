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


def test_create_subject(test_subject):
    request_data = {
        "name": "Physics"
    }
    response = client.post('/admin/subjects', json=request_data)
    db = TestingSessionLocal()
    model = db.query(Subject).filter(Subject.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert model.name == request_data.get('name')


def test_show_all_subjects(test_subject):
    response = client.get('/admin/subjects')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'name': 'Math'}]


def test_show_all_subjects_without_subjects():
    response = client.get('/admin/subjects')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_edit_subject(test_subject):
    request_data = {
        'name': 'Physics'
    }
    response = client.put('/admin/subjects/1', json=request_data)
    db = TestingSessionLocal()
    model = db.query(Subject).filter(Subject.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.name == request_data.get('name')


def test_edit_subject_not_exist_subject():
    request_data = {
        'name': 'Physics'
    }
    response = client.put('/admin/subjects/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_delete_subject(test_subject):
    response = client.delete('/admin/subjects/1')
    db = TestingSessionLocal()
    model = db.query(Subject).filter(Subject.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model is None


def test_delete_subject_not_exist_subject():
    response = client.delete('/admin/subjects/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_delete_subject_related_grades_error(test_grade):
    response = client.delete('/admin/subjects/1')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Subject with id: 1 cannot be deleted because it is associated with table: '
                                         'grades.'}


def test_delete_subject_related_attendance_error(test_attendance):
    response = client.delete('/admin/subjects/1')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Subject with id: 1 cannot be deleted because it is associated with table: attendance.'}


def test_delete_subject_related_users_error(test_teacher_with_subject):
    response = client.delete('/admin/subjects/1')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Subject with id: 1 cannot be deleted because it is associated with table: users.'}
