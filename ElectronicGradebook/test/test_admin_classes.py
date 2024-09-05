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


def test_create_class(test_class):
    request_data = {
        'name': '1B'
    }
    response = client.post('/admin/classes', json=request_data)
    db = TestingSessionLocal()
    model = db.query(Class).filter(Class.id == 2).first()
    assert response.status_code == status.HTTP_201_CREATED
    assert model.name == request_data.get('name')


def test_show_all_classes(test_class):
    response = client.get('/admin/classes')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'name': '1A'}]


def test_show_all_classes_without_classes():
    response = client.get('/admin/classes')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
