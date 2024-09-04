from datetime import date
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..models import User, Class, Subject, Grade
from ..routers.auth import bcrypt_context
from sqlalchemy.pool import StaticPool

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


@pytest.mark.usefixtures("test_student", "test_subject", "test_teacher")
def test_grade():
    grade = Grade(
        student_id=1,
        subject_id=1,
        grade=5,
        date=date(2024, 9, 4),
        added_by_id=2
    )
    db = TestingSessionLocal()
    db.add(grade)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM grades"))
        connection.commit()
