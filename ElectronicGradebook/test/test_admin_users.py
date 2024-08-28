from datetime import date
from typing import Annotated
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette import status
from ..models import User, Class, Subject
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


@pytest.fixture()
def test_class():
    test_class = Class(
        name='1A'
    )
    db = TestingSessionLocal()
    db.add(test_class)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM classes"))
        connection.commit()


@pytest.fixture()
def test_subject():
    subject = Subject(
        name='Math'
    )
    db = TestingSessionLocal()
    db.add(subject)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM subjects"))
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
    assert response.json() is None
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.first_name == request_data.get('first_name')
    assert model.last_name == request_data.get('last_name')
    assert model.username == request_data.get('username')
    assert model.date_of_birth.strftime("%Y-%m-%d") == request_data.get('date_of_birth')
    assert model.role == request_data.get('role')


def test_add_student_with_class(test_student, test_class):
    request_data = {
        'first_name': 'Andrzej',
        'last_name': 'Kowalski',
        'username': 'a_kowalski',
        'password': 'test1234',
        'date_of_birth': '2006-12-06',
        'class_id': 1,
        'role': 'student'
    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is None
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.first_name == request_data.get('first_name')
    assert model.last_name == request_data.get('last_name')
    assert model.username == request_data.get('username')
    assert model.date_of_birth.strftime("%Y-%m-%d") == request_data.get('date_of_birth')
    assert model.class_id == request_data.get('class_id')
    assert model.role == request_data.get('role')


def test_add_teacher_with_subject(test_teacher, test_subject):
    request_data = {
        'first_name': 'Janina',
        'last_name': 'Borkowska',
        'username': 'j_borkowska',
        'password': 'test1234',
        'date_of_birth': '1987-04-07',
        'subject_id': 1,
        'role': 'teacher'
    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is None


def test_add_user_invalid_role():
    request_data = {
        'first_name': 'Andrzej',
        'last_name': 'Kowalski',
        'username': 'a_kowalski',
        'password': 'test1234',
        'date_of_birth': '2006-12-06',
        'role': 'tchr'
    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Invalid role: tchr. Allowed roles are 'admin', 'teacher','student'."}


def test_add_user_username_exist(test_student):
    request_data = {
        'first_name': 'Andrzej',
        'last_name': 'Kowalski',
        'username': 'j_bravo',
        'password': 'test1234',
        'date_of_birth': '2006-12-06',
        'role': 'student'
    }
    response = client.post("admin/add-user", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': "Username: 'j_bravo' already exist."}


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
    assert student_data['id'] == 1
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
    assert teacher_data['id'] == 1
    assert teacher_data['first_name'] == 'Anna'
    assert teacher_data['last_name'] == 'Kowalska'
    assert teacher_data['username'] == 'a_kowalska'
    assert teacher_data['role'] == 'teacher'


def test_show_student_detail(test_student):
    response = client.get('admin/students/?username=j_bravo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    students = response.json()
    student_data = next((student for student in students))
    assert student_data['id'] == 1
    assert student_data['first_name'] == 'Johny'
    assert student_data['last_name'] == 'Bravo'
    assert student_data['username'] == 'j_bravo'
    assert student_data['date_of_birth'] == '2024-08-18'
    assert student_data['class'] == 'No class assigned'
    assert student_data['role'] == 'student'


def test_show_student_detail_username_not_found():
    response = client.get('admin/students/?username=b_bbb')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with username: b_bbb not found'}


def test_show_teacher_detail(test_teacher):
    response = client.get('admin/teachers/?username=a_kowalska')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    teachers = response.json()
    teacher_data = next((teacher for teacher in teachers))
    assert teacher_data['id'] == 1
    assert teacher_data['first_name'] == 'Anna'
    assert teacher_data['last_name'] == 'Kowalska'
    assert teacher_data['username'] == 'a_kowalska'
    assert teacher_data['subject'] == 'No subject assigned'
    assert teacher_data['role'] == 'teacher'


def test_show_teacher_detail_username_not_found():
    response = client.get('admin/teachers/?username=a_aaa')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with username: a_aaa not found'}


def test_edit_user(test_student):
    request_data = {
        'first_name': 'Andrzej',
        'last_name': 'Kowalski',
        'username': 'a_kowalski'
    }
    response = client.put('admin/edit-user/?username=j_bravo', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(User).filter(User.username == 'a_kowalski').first()
    assert model.first_name == request_data.get('first_name')
    assert model.last_name == request_data.get('last_name')
    assert model.username == request_data.get('username')
