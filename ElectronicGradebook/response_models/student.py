def map_student_profile_to_response(student):
    return {
        'first_name': student.first_name,
        'last_name': student.last_name,
        'username': student.username,
        'date_of_birth': student.date_of_birth,
        'class': student.klasa.name if student.klasa else "No class assigned",
        'role': student.role
    }


def map_student_grade_to_response(grades):
    student_grades = {}
    for grade in grades:
        subject_name = grade.subject.name
        teacher = grade.teacher
        added_by = f"{teacher.first_name} {teacher.last_name}"

        student_grades.setdefault(subject_name, []).append({
            'grade': grade.grade,
            'date': grade.date,
            'added_by': added_by
        })

    return student_grades
