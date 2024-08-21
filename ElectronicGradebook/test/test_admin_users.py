from datetime import date
from typing import Annotated
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette import status
from ..models import User
from ..database import Base
from ..routers.auth import get_db, get_current_user, bcrypt_context
from ..main import app

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'test', 'id': 1, 'role': 'admin'}


@pytest.fixture
def test_student():
    student = User(
        first_name='Johny',
        last_name='Bravo',
        username='j_bravo',
        hashed_password=bcrypt_context.hash('test1234'),
        date_of_birth=date(2024, 8, 18),
        role='student'
    )
    db = TestingSessionLocal()
    db.add(student)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture()
def test_teacher():
    teacher = User(
        first_name='Anna',
        last_name='Kowalska',
        username='a_kowalska',
        hashed_password=bcrypt_context.hash('test1234'),
        date_of_birth=date(2002, 7, 2),
        role='teacher'
    )
    db = TestingSessionLocal()
    db.add(teacher)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
user_dependency = Annotated[dict, Depends(get_current_user)]

client = TestClient(app)


def test_add_student(test_student):
    request_data = {
        'first_name': 'Andrzej',
        'last_name': 'Kowalski',
        'username': 'a_kowalski',
        'password': 'test1234',
        'date_of_birth': '2006-12-06',
        'role': 'student'
    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == None


def test_add_student_class_not_exist():
    request_data = {
        'first_name': 'Marcin',
        'last_name': 'Balcerowicz',
        'username': 'm_balcerowicz',
        'password': 'test1234',
        'date_of_birth': '2002-07-02',
        'class_id': 999,
        'role': 'student'

    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Class with id: 999 does not exist'}


def test_add_teacher_subject_not_exist():
    request_data = {
        'first_name': 'Jan',
        'last_name': 'Kujawa',
        'username': 'j_kujawa',
        'password': 'test1234',
        'date_of_birth': '1990-03-12',
        'subject_id': 999,
        'role': 'teacher'
    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_show_all_students(test_student):
    response = client.get('admin/students')
    assert response.status_code == status.HTTP_200_OK
    students = response.json()
    assert len(students) > 0
    student_data = next((student for student in students if student['username'] == 'j_bravo'), None)
    assert student_data is not None
    assert student_data['first_name'] == 'Johny'
    assert student_data['last_name'] == 'Bravo'
    assert student_data['username'] == 'j_bravo'
    assert student_data['date_of_birth'] == '2024-08-18'
    assert student_data['role'] == 'student'


def test_show_all_teachers(test_teacher):
    response = client.get('admin/teachers')
    assert response.status_code == status.HTTP_200_OK
    teachers = response.json()
    assert len(teachers) > 0
    teacher_data = next((teacher for teacher in teachers if teacher['username'] == 'a_kowalska'), None)
    assert teacher_data is not None
    assert teacher_data['first_name'] == 'Anna'
    assert teacher_data['last_name'] == 'Kowalska'
    assert teacher_data['username'] == 'a_kowalska'
    assert teacher_data['role'] == 'teacher'
