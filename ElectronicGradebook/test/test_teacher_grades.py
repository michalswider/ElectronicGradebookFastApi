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
