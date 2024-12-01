def map_student_attendance_to_response(attendance_model):
    student_attendance = {}
    for attendance in attendance_model:
        subject_name = attendance.subject.name
        teacher = attendance.teacher
        added_by = f"{teacher.first_name} {teacher.last_name}"

        student_attendance.setdefault(subject_name,[]).append({
            'id': attendance.id,
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': added_by

        })
    return student_attendance


def map_attendance_for_class_on_date_to_response(attendance_model):
    result = {}
    for attendance in attendance_model:
        student = attendance.student
        teacher = attendance.teacher
        attendance_class = student.klasa.name
        attendance_subject = attendance.subject.name
        attendance_student = f"{student.first_name} {student.last_name}"
        added_by = f"{teacher.first_name} {teacher.last_name}"

        result.setdefault(attendance_class, {}).setdefault(attendance_subject, {}).setdefault(attendance_student,
                                                                                              []).append({
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': added_by
        })

    return result

def map_attendance_for_student_in_subject(attendance_model):
    result = []
    for attendance in attendance_model:
        result.append({
            'id': attendance.id,
            'class_date': attendance.class_date,
            'status': attendance.status,
            'added_by': attendance.teacher.first_name + " " + attendance.teacher.last_name
        })
    return result
