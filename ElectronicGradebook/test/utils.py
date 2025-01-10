from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..models import Attendance, Class, Grade, Subject, User
from ..routers.auth import bcrypt_context, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_authorization_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def token():
    data_user = {"username": "test", "id": 1, "role": "admin"}
    return create_access_token(
        username=data_user.get("username"),
        user_id=data_user.get("id"),
        role=data_user.get("role"),
        expires_delta=timedelta(minutes=20),
    )


@pytest.fixture
def test_student():
    student = User(
        first_name="Johny",
        last_name="Bravo",
        username="j_bravo",
        hashed_password=bcrypt_context.hash("test1234"),
        date_of_birth=date(2024, 8, 18),
        role="student",
    )
    db = TestingSessionLocal()
    db.add(student)
    db.commit()
    yield student
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture
def test_student_with_class(test_class):
    student = User(
        first_name="Johny",
        last_name="Bravo",
        username="j_bravo",
        hashed_password=bcrypt_context.hash("test1234"),
        date_of_birth=date(2024, 8, 18),
        class_id=1,
        role="student",
    )
    db = TestingSessionLocal()
    db.add(student)
    db.commit()
    yield student
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture()
def test_teacher():
    teacher = User(
        first_name="Anna",
        last_name="Kowalska",
        username="a_kowalska",
        hashed_password=bcrypt_context.hash("test1234"),
        date_of_birth=date(2002, 7, 2),
        role="teacher",
    )
    db = TestingSessionLocal()
    db.add(teacher)
    db.commit()
    yield teacher
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture()
def test_teacher_with_subject(test_subject):
    teacher = User(
        first_name="Anna",
        last_name="Kowalska",
        username="a_kowalska",
        hashed_password=bcrypt_context.hash("test1234"),
        date_of_birth=date(2002, 7, 2),
        subject_id=1,
        role="teacher",
    )
    db = TestingSessionLocal()
    db.add(teacher)
    db.commit()
    yield teacher
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture()
def test_class():
    test_class = Class(name="1A")
    db = TestingSessionLocal()
    db.add(test_class)
    db.commit()
    yield test_class
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM classes"))
        connection.commit()


@pytest.fixture()
def test_subject():
    subject = Subject(name="Math")
    db = TestingSessionLocal()
    db.add(subject)
    db.commit()
    yield subject
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM subjects"))
        connection.commit()


@pytest.fixture()
def test_subject2():
    subject = Subject(name="Physics")
    db = TestingSessionLocal()
    db.add(subject)
    db.commit()
    yield subject
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM subjects"))
        connection.commit()


@pytest.fixture()
def test_grade(test_student_with_class, test_subject, test_teacher):
    grade = Grade(
        student_id=1, subject_id=1, grade=5, date=date(2024, 9, 4), added_by_id=2
    )
    db = TestingSessionLocal()
    db.add(grade)
    db.commit()
    yield grade
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM grades"))
        connection.commit()


@pytest.fixture()
def test_attendance(test_student_with_class, test_subject, test_subject2, test_teacher):
    attendance = Attendance(
        student_id=1,
        subject_id=1,
        class_date=date(2024, 9, 4),
        status="present",
        added_by_id=2,
    )
    db = TestingSessionLocal()
    db.add(attendance)
    db.commit()
    yield attendance
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM attendance"))
        connection.commit()
