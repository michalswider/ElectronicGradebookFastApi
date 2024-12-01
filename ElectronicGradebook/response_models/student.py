def map_student_profile_to_response(student):
    return {
        'first_name': student.first_name,
        'last_name': student.last_name,
        'username': student.username,
        'date_of_birth': student.date_of_birth,
        'class': student.klasa.name if student.klasa else "No class assigned",
        'role': student.role
    }