from datetime import date


class ApplicationException(Exception):
    def __init__(self, detail: str, user: str):
        self.detail = detail
        self.user = user
        super().__init__(self.detail, self.user)


class InvalidException(Exception):
    def __init__(self, detail: str, user: str):
        self.detail = detail
        self.user = user
        super().__init__(self.detail, self.user)


class ClassNotExistException(ApplicationException):
    def __init__(self, class_id: int, username: str):
        super().__init__(f'Class with id: {class_id} does not exist', f'User: {username}')
        self.class_id = class_id
        self.username = username


class SubjectNotExistException(ApplicationException):
    def __init__(self, subject_id: int, username: str):
        super().__init__(f'Subject with id: {subject_id} does not exist', f'User: {username}')
        self.subject_id = subject_id
        self.username = username


class UsernameAlreadyExistException(InvalidException):
    def __init__(self, username: str, user: str):
        super().__init__(f"Username: '{username}' already exist.", f'User: {username}')
        self.username = username
        self.user = user


class InvalidRoleException(InvalidException):
    def __init__(self, role: str, username: str):
        super().__init__(f"Invalid role: {role}. Allowed roles are 'admin', 'teacher','student'.", f'User: {username}')
        self.role = role
        self.username = username


class UsernameNotFoundException(ApplicationException):
    def __init__(self, username: str, user: str):
        super().__init__(f'User with username: {username} not found', f'User: {username}')
        self.username = username
        self.user = user


class UserIdNotFoundException(ApplicationException):
    def __init__(self, user_id: int, username: str):
        super().__init__(f'User with id: {user_id} not found', f'User: {username}')
        self.user_id = user_id
        self.username = username


class GradesNotFoundException(ApplicationException):
    def __init__(self, student_id: int, username: str):
        super().__init__(f'Grades for user with id: {student_id} not found', f'User: {username}')
        self.student_id = student_id
        self.username = username


class GradeEditNotExistException(ApplicationException):
    def __init__(self, student_id: int, subject_id: int, grade_id: int, username: str):
        super().__init__(f'Grade with id: {grade_id} not found, for user id: {student_id} on subject id: {subject_id}',
                         f'User: {username}')
        self.student_id = student_id
        self.subject_id = subject_id
        self.grade_id = grade_id
        self.username = username


class GradeForSubjectNotExistException(ApplicationException):
    def __init__(self, class_id: int, subject_id: int, username: str):
        super().__init__(f'No grades found for class id: {class_id} and subject id: {subject_id}', f'User: {username}')
        self.class_id = class_id
        self.subject_id = subject_id
        self.username = username


class AverageByClassNotFoundException(ApplicationException):
    def __init__(self, class_id: int, username: str):
        super().__init__(f'No average found for class id: {class_id}.', f'User: {username}')
        self.class_id = class_id
        self.username = username


class AverageBySubjectForStudentNotFoundException(ApplicationException):
    def __init__(self, subject_id: int, student_id: int, username: str):
        super().__init__(f'No average found for subject id: {subject_id} and student id: {student_id}.',
                         f'User: {username}')
        self.subject_id = subject_id
        self.student_id = student_id
        self.username = username


class InvalidStatusException(InvalidException):
    def __init__(self, status: str, username: str):
        super().__init__(f"Invalid status: {status}. Allowed status are 'present', 'absent', 'excused'.",
                         f'User: {username}')
        self.status = status
        self.username = username


class StudentAttendanceNotFoundException(ApplicationException):
    def __init__(self, student_id: int, username: str):
        super().__init__(f'No attendance records found for student with id: {student_id}', f'User: {username}')
        self.student_id = student_id
        self.username = username


class ClassAttendanceOnDateNotFoundException(ApplicationException):
    def __init__(self, class_id: int, date: date, username: str):
        super().__init__(f'No attendance records found for class with id: {class_id} on date: {date}',
                         f'User: {username}')
        self.class_id = class_id
        self.date = date
        self.username = username


class AttendanceForStudentInSubjectNotFoundException(ApplicationException):
    def __init__(self, subject_id: int, student_id: int, username: str):
        super().__init__(
            f'No attendance records found for student with id: {student_id} in subject with id: {subject_id}',
            f'User: {username}')
        self.subject_id = subject_id
        self.student_id = student_id
        self.username = username


class AttendanceDataNotFoundException(ApplicationException):
    def __init__(self, attendance_id: int, subject_id: int, student_id: int, username: str):
        super().__init__(
            f'No attendance data found for attendance_id: {attendance_id}, subject_id: {subject_id}, student_id: {student_id}',
            f'User: {username}')
        self.attendance_id = attendance_id
        self.subject_id = subject_id
        self.student_id = student_id
        self.username = username


class SubjectDeleteException(InvalidException):
    def __init__(self, subject_id: int, table_name: str, username: str):
        super().__init__(
            f'Subject with id: {subject_id} cannot be deleted because it is associated with table: {table_name}.',
            f'User: {username}')
        self.subject_id = subject_id
        self.table_name = table_name
        self.username = username


class ClassDeleteException(InvalidException):
    def __init__(self, class_id: int, table_name: str, username: str):
        super().__init__(
            f'Class with id: {class_id} cannot be deleted because it is associated with table: {table_name}.',
            f'User: {username}')
        self.class_id = class_id
        self.table_name = table_name
        self.username = username


class UserDeleteException(InvalidException):
    def __init__(self, user_id: int, table_name: str, username: str):
        super().__init__(
            f'User with id: {user_id} cannot be deleted because it is associated with table: {table_name}.',
            f'User: {username}')
        self.user_id = user_id
        self.table_name = table_name
        self.username = username
