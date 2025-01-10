def map_student_to_response(student):
    return {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "username": student.username,
        "hashed_password": student.hashed_password,
        "date_of_birth": student.date_of_birth,
        "class": student.klasa.name if student.klasa else "No class assigned",
        "role": student.role,
    }


def map_teacher_to_response(teacher):
    return {
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "username": teacher.username,
        "hashed_password": teacher.hashed_password,
        "subject": teacher.subject.name if teacher.subject else "No subject assigned",
        "role": teacher.role,
    }
