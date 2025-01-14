from datetime import date
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..exception import (ExistException, ForeignKeyConstraintException,
                         InvalidException, NotFoundException)
from ..models import Attendance, Class, Grade, Subject, User
from ..routers.auth import bcrypt_context, get_db
from ..schemas.students import UserVerification

db_dependency = Annotated[Session, Depends(get_db)]


def verify_admin_user(user: dict):
    """
       Verifies if the given user is an admin.

       Args:
           user (dict): A dictionary containing user data.

       Raises:
           HTTPException: If the user is None or the user's role is not 'admin'.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission Denied"
        )


def verify_teacher_user(user: dict):
    """
       Verifies if the given user is a teacher.

       Args:
           user (dict): A dictionary containing user data.

       Raises:
           HTTPException: If the user is None or the user's role is not 'teacher'.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    if user.get("role") not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission Denied"
        )


def verify_student_user(user: dict):
    """
       Verifies if the given user is a student.

       Args:
           user (dict): A dictionary containing user data.

       Raises:
           HTTPException: If the user is None or the user's role is not 'student'.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    if user.get("role") not in ("admin", "student"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission Denied"
        )


def validate_username_exist(user: dict, username: str, db: db_dependency):
    """
        Validates whether a username already exists in the database.

        Args:
            user (dict): A dictionary containing information about the current user.
            username (str): The username to validate for existence.
            db (db_dependency): Database session for querying the User model.

        Raises:
            ExistException: If the provided username already exists in the database.
    """
    username_model = db.query(User).filter(User.username == username).first()
    if username_model is not None:
        raise ExistException(
            detail=f"Username: {username} already exist.", user=user["username"]
        )


def validate_class_exist(user: dict, class_id: int, db: db_dependency):
    """
        Validates whether a class with the given ID exists in the database and returns it.

        Args:
            user (dict): A dictionary containing information about the current user.
            class_id (int): The ID of the class to validate.
            db (db_dependency): Database session for querying the Class model.

        Returns:
            Class: The class object with the specified ID if it exists.

        Raises:
            ExistException: If the class with the specified ID does not exist.
    """
    classes = db.query(Class).filter(Class.id == class_id).first()
    if not classes:
        raise ExistException(
            detail=f"Class with id: {class_id} does not exist",
            user=user["username"],
        )
    return classes


def validate_subject_exist(user: dict, subject_id: int, db: db_dependency):
    """
        Validates whether a subject with the given ID exists in the database and returns it.

        Args:
            user (dict): A dictionary containing information about the current user.
            subject_id (int): The ID of the subject to validate.
            db (db_dependency): Database session for querying the Subject model.

        Returns:
            Subject: The subject object with the specified ID if it exists.

        Raises:
            ExistException: If the subject with the specified ID does not exist.
    """
    subjects = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subjects:
        raise ExistException(
            detail=f"Subject with id: {subject_id} does not exist",
            user=user["username"],
        )
    return subjects


def validate_roles(role: str, user: dict):
    """
        Validates whether the given role is allowed.

        Args:
            role (str): The role to validate. Must be one of the allowed roles: 'admin', 'teacher', 'student'.
            user (dict): A dictionary containing information about the current user.

        Raises:
            InvalidException: If the role is not one of the allowed roles.
    """
    valid_roles = ["admin", "teacher", "student"]
    if role not in valid_roles:
        raise InvalidException(
            detail=f"Invalid role: {role}. Allowed roles are 'admin', 'teacher','student'.",
            user=user["username"],
        )


def validate_username_found(user: dict, username: str, db: db_dependency, role: str):
    """
        Validates that a user with the given username exists in the database, optionally filtering by role.

        Args:
            user (dict): A dictionary containing information about the current user.
            username (str): The username to search for.
            db (db_dependency): Database session for querying the User model.
            role (str): The role to filter by. Use "all" to ignore role filtering.

        Returns:
            User: The user object with the specified username and role (if provided).

        Raises:
            NotFoundException: If no user with the given username (and role, if specified) is found.
    """
    if role == "all":
        user_model = db.query(User).filter(User.username == username).first()
    else:
        user_model = (
            db.query(User).filter(User.username == username, User.role == role).first()
        )
    if user_model is None:
        raise NotFoundException(
            detail=f"User with username: {username} not found",
            user=user["username"],
        )
    return user_model


def validate_database_relation(related_records: dict, user_id: int, user: dict):
    """
        Validates that a user can be safely deleted by checking for related records in the database.

        Args:
            related_records (dict): A dictionary where keys are table names and values are the
                                    related records. If a value is not empty,
                                    it indicates the existence of related records
                                    for that table.
                                    Example:
                                    {
                                        "grades": db.query(Grade).filter(...).first(),
                                        "attendance": db.query(Attendance).filter(...).first()
                                    }
            user_id (int): The ID of the user to validate for deletion.
            user (dict): A dictionary containing information about the current user.

        Raises:
            ForeignKeyConstraintException: If any related records are found in the `related_records` dictionary.
                                            The exception includes the table name causing the constraint.

    """
    for table_name, record in related_records.items():
        if record:
            raise ForeignKeyConstraintException(
                detail=f"User with id: {user_id} cannot be deleted because it is associated with table: {table_name}.",
                user=user["username"],
            )


def validate_database_subjects_relation(
    related_records: dict, subject_id: int, user: dict
):
    """
        Validates that a subject can be safely deleted by checking for related records in the database.

        Args:
            related_records (dict): A dictionary where keys are table names and values are the
                                    related records. If a value is not empty,
                                    it indicates the existence of related records
                                    for that table.
                                    Example:
                                    {
                                        "grades": db.query(Grade).filter(...).all(),
                                        "attendance": db.query(Attendance).filter(...).all()
                                        "users": db.query(User).filter(...).all()
                                    }
            subject_id (int): The ID of the subject to validate for deletion.
            user (dict): A dictionary containing information about the current user.

        Raises:
            ForeignKeyConstraintException: If any related records are found in the `related_records` dictionary.
                                            The exception includes the table name causing the constraint.

    """
    for table_name, record in related_records.items():
        if record:
            raise ForeignKeyConstraintException(
                f"Subject with id: {subject_id} cannot be deleted because it is associated with table: {table_name}.",
                user=user["username"],
            )


def validate_user_id(
    user_id: int,
    db: db_dependency,
    user: dict,
    role: str,
):
    """
        Validates the existence of a user with the given ID and role in the database.

        Args:
            user_id (int): The ID of the user to validate.
            db (db_dependency): The database session used to query the User model.
            user (dict): A dictionary containing information about the current user.
            role (str): The role to validate. Valid values are:
                        - "student": Checks for users with the role "student".
                        - "teacher": Checks for users with the role "teacher".
                        - "all": Checks for users regardless of their role.

        Raises:
            ValueError: If an invalid role is provided (not "student", "teacher", or "all").
            NotFoundException: If no user is found matching the provided ID and role.
   """
    if role == "student":
        user_model = (
            db.query(User).filter(User.id == user_id, User.role == "student").first()
        )
    elif role == "teacher":
        user_model = (
            db.query(User).filter(User.id == user_id, User.role == "teacher").first()
        )
    elif role == "all":
        user_model = db.query(User).filter(User.id == user_id).first()
    else:
        raise ValueError(
            f"Invalid user type: {role}. Allowed types are 'student','teacher','all'."
        )
    if user_model is None:
        raise NotFoundException(
            detail=f"User with id: {user_id} not found", user=user["username"]
        )


def validate_related_class(
    class_id: int, user: dict, db: db_dependency, table_name: str
):
    """
        Validates that a class can be safely deleted by checking for related records from table users.

        Args:
            class_id (int): The ID of the class to validate for deletion.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `User` model.
            table_name (str): The name of the table causing the constraint. Included in the exception message.

        Raises:
            ForeignKeyConstraintException: If related users are found in the `User` table associated with the given `class_id`.

    """
    related_users = db.query(User).filter(User.class_id == class_id).all()
    if related_users:
        raise ForeignKeyConstraintException(
            f"Class with id: {class_id} cannot be deleted because it is associated with table: {table_name}.",
            user=user["username"],
        )


def validate_user_grades(student_id: int, user: dict, db: db_dependency, role: str):
    """
        Validates the existence of grades for a user.

        Args:
            student_id (int): The ID of the student whose grades are to be validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `User`, `Subject`, and `Grade` models.
            role (str): The role of the user, which determines the specific exception message.

        Returns:
            List[Grade]: A list of grade records associated with the student ID if they exist.

        Raises:
            NotFoundException:
                - For "admin" or "teacher": If no user or grades are found matching the provided student ID.
                - For "student": If the student has no grades.

    """
    grades = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .filter(Grade.student_id == student_id)
        .all()
    )

    if not grades:
        if role in ["admin", "teacher"]:
            raise NotFoundException(
                detail=f"Grades for user with id: {student_id} not found",
                user=user["username"],
            )
        elif role == "student":
            raise NotFoundException(detail="Not found", user=user["username"])
    return grades


def validate_grades_for_subject(
    subject_id: int, class_id: int, user: dict, db: db_dependency
):
    """
        Validates the existence of grades for a specific subject and class.

        Args:
            subject_id (int): The ID of the subject whose grades are to be validated.
            class_id (int): The ID of the class whose grades are to be validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `User`, `Subject`, and `Grade` models.

        Returns:
            List[Grade]: A list of grade records associated with the subject ID and class ID if they exist.

        Raises:
            NotFoundException: If no grades are found matching the provided subject ID and class ID.
    """
    grade_model = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .join(Class, User.class_id == Class.id)
        .filter(Class.id == class_id, Grade.subject_id == subject_id)
        .all()
    )
    if not grade_model:
        raise NotFoundException(
            detail=f"No grades found for class id: {class_id} and subject id: {subject_id}",
            user=user["username"],
        )
    return grade_model


def validate_average_student_for_subject(
    subject_id: int, student_id: int, user: dict, db: db_dependency
):
    """
        Validates the existence of grades for calculating a student's average in a specific subject.

        Args:
            subject_id (int): The ID of the subject for which the student's average grades are to be validated.
            student_id (int): The ID of the student whose grades are to be checked.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `Grade` model.

        Returns:
            List[Grade]: A list of grade records associated with the subject ID and student ID if they exist.

        Raises:
            NotFoundException: If no grades are found for the given subject ID and student ID.
    """
    grade_model = (
        db.query(Grade)
        .filter(Grade.student_id == student_id, Grade.subject_id == subject_id)
        .all()
    )
    if not grade_model:
        raise NotFoundException(
            detail=f"No average found for subject id: {subject_id} and student id: {student_id}.",
            user=user["username"],
        )
    return grade_model


def validate_average_by_class(class_id: int, user: dict, db: db_dependency):
    """
        Validates the existence of grades for calculating the average in a specific class.

        Args:
            class_id (int): The ID of the class for which the average grades are to be validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `User`,`Grade` and `Class` model.

        Returns:
            List[Grade]: A list of grade records associated with the specified class ID if they exist.

        Raises:
            NotFoundException: If no grades are found for the given class ID.
    """
    grades = (
        db.query(Grade)
        .join(User, Grade.student_id == User.id)
        .join(Class, Class.id == User.class_id)
        .filter(Class.id == class_id)
        .all()
    )
    if not grades:
        raise NotFoundException(
            detail=f"No average found for class id: {class_id}.",
            user=user["username"],
        )
    return grades


def validate_grade_edit(
    subject_id: int, grade_id: int, student_id: int, user: dict, db: db_dependency
):
    """
        Validates the existence of a grade for editing.

        Args:
            subject_id (int): The ID of the subject associated with the grade to be validated.
            grade_id (int): The ID of the grade to be validated for editing.
            student_id (int) The ID of the student whose grade is being validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `Grade` model.

        Returns:
            Grade: The grade record if it exists and matches the provided criteria.

        Raises:
            NotFoundException: If no grade is found matching the provided grade ID, subject ID, and student ID.
    """
    grade_model = (
        db.query(Grade)
        .filter(
            Grade.student_id == student_id,
            Grade.subject_id == subject_id,
            Grade.id == grade_id,
        )
        .first()
    )
    if grade_model is None:
        raise NotFoundException(
            detail=f"Grade with id: {grade_id} not found, for user id: {student_id} on subject id: {subject_id}",
            user=user["username"],
        )
    return grade_model


def validate_grade_delete(
    subject_id: int, grade_id: int, student_id: int, user: dict, db: db_dependency
):
    """
        Validates the existence of a grade for deletion.

        Args:
            subject_id (int): The ID of the subject associated with the grade to be validated.
            grade_id (int): The ID of the grade to be validated for deletion.
            student_id (int) The ID of the student whose grade is being validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `Grade` model.

        Returns:
            Grade: The grade record if it exists and matches the provided criteria.

        Raises:
            NotFoundException: If no grade is found matching the provided grade ID, subject ID, and student ID.
    """
    grade_model = (
        db.query(Grade)
        .filter(
            Grade.student_id == student_id,
            Grade.id == grade_id,
            Grade.subject_id == subject_id,
        )
        .first()
    )
    if grade_model is None:
        raise NotFoundException(
            detail="Grade with the specified student_id, subject_id, and grade_id not found",
            user=user["username"],
        )
    return grade_model


def validate_attendance_status(attendance_status: str, user: dict):
    """
        Validates the `attendance_status` value.

        Args:
            attendance_status (str): The attendance status to validate.
                                    Must be one of 'present', 'absent', or 'excused'.
            user (dict): A dictionary containing information about the current user.

        Raises:
            InvalidException: If `attendance_status` is not one of 'present', 'absent', or 'excused'.
    """
    if attendance_status not in ("present", "absent", "excused"):
        raise InvalidException(
            detail=f"Invalid status: {attendance_status}. Allowed status are 'present', 'absent', 'excused'.",
            user=user["username"],
        )


def validate_student_attendance(
    student_id: int, db: db_dependency, user: dict, role: str
):
    """
        Validates the existence of attendance records for a student.

        Args:
            student_id (int): The ID of the student whose attendance records are being validated.
            db (db_dependency): The database session used to query the `Attendance`,`User` and `Subject` models.
            user (dict): A dictionary containing information about the current user.
            role (str): The role of the current user. Used to customize exception messages.

        Returns:
            List[Attendance]: A list of attendance records for the specified student ID.

        Raises:
            NotFoundException:
                - for "admin" or "teacher": Raised if no attendance records are found for the student ID.
                - for "student": Raised if the current student has no attendance records.
    """
    attendance_model = (
        db.query(Attendance)
        .join(User, Attendance.student_id == User.id)
        .join(Subject, Attendance.subject_id == Subject.id)
        .filter(Attendance.student_id == student_id)
        .all()
    )
    if not attendance_model:
        if role in ["admin", "teacher"]:
            raise NotFoundException(
                detail=f"No attendance records found for student with id: {student_id}",
                user=user["username"],
            )
        elif role == "student":
            raise NotFoundException(detail="Not found", user=user["username"])
    return attendance_model


def validate_attendance_for_class_on_date(
    class_id: int, date: date, user: dict, db: db_dependency
):
    """
        Validates the existence of attendance records for a class on a specific date.

        Args:
            class_id (int): The ID of the class whose attendance records are being validated.
            date (date): The specific date for which attendance is being validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `Attendance`,`User` and `Class` models.

        Returns:
            List[Attendance]: A list of attendance records for the specified class ID and date.

        Raises:
            NotFoundException: If no attendance records are found matching the provided class ID and date.
    """
    attendance_model = (
        db.query(Attendance)
        .join(User, Attendance.student_id == User.id)
        .join(Class, Class.id == User.class_id)
        .filter(Attendance.class_date == date, Class.id == class_id)
        .all()
    )
    if not attendance_model:
        raise NotFoundException(
            detail=f"No attendance records found for class with id: {class_id} on date: {date}",
            user=user["username"],
        )
    return attendance_model


def validate_attendance_for_student_in_subject(
    student_id: int, subject_id: int, user: dict, db: db_dependency
):
    """
        Validates the existence of attendance records for a student in a specific subject.

        Args:
            student_id (int): The ID of the student whose attendance records are being validated.
            subject_id (int): The ID of the subject for which attendance is being validated.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `Attendance`,`User` and `Subject` models.

        Returns:
            List[Attendance]: A list of attendance records for the specified student ID and subject ID.

        Raises:
            NotFoundException: If no attendance records are found matching the provided student ID and subject ID.
    """
    attendance_model = (
        db.query(Attendance)
        .join(User, User.id == Attendance.student_id)
        .join(Subject, Subject.id == Attendance.subject_id)
        .filter(
            Attendance.subject_id == subject_id, Attendance.student_id == student_id
        )
        .all()
    )

    if not attendance_model:
        raise NotFoundException(
            detail=f"No attendance records found for student with id: {student_id} in subject with id: {subject_id}",
            user=user["username"],
        )
    return attendance_model


def validate_attendance_data(
    attendance_id: int, student_id: int, subject_id: int, user: dict, db: db_dependency
):
    """
        Validates the existence of specific attendance data for a given student and subject.

        Args:
            attendance_id (int): The ID of the attendance record to validate.
            student_id (int): The ID of the student associated with the attendance record.
            subject_id (int): The ID of the subject associated with the attendance record.
            user (dict): A dictionary containing information about the current user.
            db (db_dependency): The database session used to query the `Attendance` model.

        Returns:
            Attendance: The attendance record if it exists and matches the provided criteria.

        Raises:
            NotFoundException: If no attendance record is found matching the provided IDs.
    """
    attendance_model = (
        db.query(Attendance)
        .filter(
            Attendance.id == attendance_id,
            Attendance.student_id == student_id,
            Attendance.subject_id == subject_id,
        )
        .first()
    )
    if attendance_model is None:
        raise NotFoundException(
            detail=f"No attendance data found for attendance_id: {attendance_id}, subject_id: {subject_id}, student_id: {student_id}",
            user=user["username"],
        )
    return attendance_model


def validate_password_reset(
    request: UserVerification, student_id: int, db: db_dependency
):
    """
        Validates the existence and correctness of the old password for resetting it.

        Args:
            request: The request object containing the old password to verify and the new password.
            student_id (int): The ID of the student whose password is being reset.
            db (db_dependency): The database session used to query the `User` model.

        Returns:
            User: The user object if the old password is successfully verified.

        Raises:
            HTTPException: If the old password does not match the hashed password
                        stored in the database, an exception with status code 401
                        is raised.
    """
    user_model = db.query(User).filter(User.id == student_id).first()
    if not bcrypt_context.verify(request.old_password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change"
        )
    return user_model
