from starlette import status
from starlette.testclient import TestClient
from ..main import app
from .utils import *
from ..routers.auth import get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_class(token, test_class):
    request_data = {
        'name': '1B'
    }
    response = client.post('/admin/classes', json=request_data, headers=get_authorization_header(token))
    db = TestingSessionLocal()
    model = db.query(Class).filter(Class.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert model.name == request_data.get('name')


def test_show_all_classes(token, test_class):
    response = client.get('/admin/classes', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'name': '1A'}]


def test_show_all_classes_without_classes(token):
    response = client.get('/admin/classes', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_edit_class(token, test_class):
    request_data = {
        'name': '1B'
    }
    response = client.put('/admin/classes/1', json=request_data, headers=get_authorization_header(token))
    db = TestingSessionLocal()
    model = db.query(Class).filter(Class.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.name == request_data.get('name')


def test_edit_class_not_exist_class(token):
    request_data = {
        'name': '1B'
    }
    response = client.put('/admin/classes/999', json=request_data, headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Class with id: 999 does not exist'}


def test_delete_class(token, test_class):
    response = client.delete('/admin/classes/1', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Class).filter(Class.id == 1).first()
    assert model is None


def test_delete_class_related_users_error(token, test_student_with_class):
    response = client.delete('admin/classes/1', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        'detail': 'Class with id: 1 cannot be deleted because it is associated with table: users.'}


def test_delete_class_not_exist_class(token):
    response = client.delete('admin/classes/999', headers=get_authorization_header(token))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Class with id: 999 does not exist'}
