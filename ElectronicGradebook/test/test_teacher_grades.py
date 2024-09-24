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


def test_show_student_grades_user_id_not_found():
    response = client.get('teacher/grades/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}


def test_show_student_grades_not_found(test_student, test_subject):
    response = client.get('teacher/grades/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Grades for user with id: 1 not found'}


def test_get_students_grades_for_subject(test_grade):
    response = client.get('teacher/grades/class/1/subject/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'Johny Bravo': [{'id': 1, 'grade': 5, 'date': '2024-09-04', 'added_by': 'Anna Kowalska'}]}


def test_get_students_grades_for_subject_class_not_exist():
    response = client.get('teacher/grades/class/999/subject/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Class with id: 999 does not exist'}


def test_get_students_grades_for_subject_not_exist(test_class):
    response = client.get('teacher/grades/class/1/subject/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_get_students_grades_for_subject_grades_not_found(test_class, test_subject):
    response = client.get('teacher/grades/class/1/subject/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No grades found for class id: 1 and subject id: 1'}


def test_show_average_student_for_subject(test_grade):
    response = client.get('teacher/grades/average/subject/1?student_id=1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'average_grade': 5.0}


def test_show_average_student_for_subject_not_exist():
    response = client.get('teacher/grades/average/subject/999?student_id=1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_show_average_student_for_subject_user_id_not_found(test_subject):
    response = client.get('teacher/grades/average/subject/1?student_id=999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}


def test_show_average_student_for_subject_average_not_found(test_student, test_subject):
    response = client.get('teacher/grades/average/subject/1?student_id=1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No average found for subject id: 1 and student id: 1.'}


def test_show_average_by_class(test_grade):
    response = client.get('teacher/grades/average/class/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'class': '1A', 'average_grade': 5.0}


def test_show_average_by_class_not_exist():
    response = client.get('teacher/grades/average/class/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Class with id: 999 does not exist'}


def test_show_average_by_class_average_not_found(test_class):
    response = client.get('teacher/grades/average/class/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No average found for class id: 1.'}


def test_edit_student_grade(test_grade):
    request_data = {
        'grade': 1,
        'date': '2024-09-20'
    }
    response = client.put('teacher/grades/1?subject_id=1&grade_id=1', json=request_data)
    db = TestingSessionLocal()
    model = db.query(Grade).filter(Grade.id == 1, Grade.subject_id == 1, Grade.student_id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.grade == request_data.get('grade')
    assert model.date.strftime("%Y-%m-%d") == request_data.get('date')


def test_edit_student_grade_user_id_not_found():
    request_data = {
        'grade': 1,
        'date': '2024-09-20'
    }
    response = client.put('teacher/grades/999?subject_id=1&grade_id=1', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}


def test_edit_student_grade_subject_not_exist(test_student):
    request_data = {
        'grade': 1,
        'date': '2024-09-20'
    }
    response = client.put('teacher/grades/1?subject_id=999&grade_id=1', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Subject with id: 999 does not exist'}


def test_edit_student_grade_not_found(test_student, test_subject):
    request_data = {
        'grade': 1,
        'date': '2024-09-20'
    }
    response = client.put('teacher/grades/1?subject_id=1&grade_id=999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Grade with id: 999 not found, for user id: 1 on subject id: 1'}


def test_delete_grade(test_grade):
    response = client.delete('teacher/grades/1/1/1')
    db = TestingSessionLocal()
    model = db.query(Grade).filter(Grade.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model is None


def test_delete_grade_user_id_not_found():
    response = client.delete('teacher/grades/999/1/1')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User with id: 999 not found'}
