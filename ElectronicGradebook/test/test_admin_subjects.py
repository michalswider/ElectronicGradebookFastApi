from starlette import status
from starlette.testclient import TestClient
from ..main import app
from .utils import *
from ..routers.auth import get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_subject(token, test_subject):
    request_data = {
        "name": "Physics"
    }
    response = client.post('/admin/subjects', json=request_data, headers=get_authorization_header(token))
    db = TestingSessionLocal()
    model = db.query(Subject).filter(Subject.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert model.name == request_data.get('name')


def test_show_all_subjects(token, test_subject):
    response = client.get('/admin/subjects', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'name': 'Math'}]


def test_show_all_subjects_without_subjects(token):
    response = client.get('/admin/subjects', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_edit_subject(token, test_subject):
    request_data = {
        'name': 'Physics'
    }
    response = client.put('/admin/subjects/1', json=request_data, headers=get_authorization_header(token))
    db = TestingSessionLocal()
    model = db.query(Subject).filter(Subject.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.name == request_data.get('name')


def test_edit_subject_not_exist_subject(token):
    request_data = {
        'name': 'Physics'
    }
    response = client.put('/admin/subjects/999', json=request_data, headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_delete_subject(token, test_subject):
    response = client.delete('/admin/subjects/1', headers=get_authorization_header(token))
    db = TestingSessionLocal()
    model = db.query(Subject).filter(Subject.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model is None


def test_delete_subject_not_exist_subject(token):
    response = client.delete('/admin/subjects/999', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_delete_subject_related_grades_error(token, test_grade):
    response = client.delete('/admin/subjects/1', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Subject with id: 1 cannot be deleted because it is associated with table: '
                                         'grades.'}


def test_delete_subject_related_attendance_error(token, test_attendance):
    response = client.delete('/admin/subjects/1', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        'detail': 'Subject with id: 1 cannot be deleted because it is associated with table: attendance.'}


def test_delete_subject_related_users_error(token, test_teacher_with_subject):
    response = client.delete('/admin/subjects/1', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        'detail': 'Subject with id: 1 cannot be deleted because it is associated with table: users.'}
