def map_student_attendance_to_response(attendance_model):
    student_attendance = {
        subject_name: [
            {
                'id': attendance.id,
                'class_date': attendance.class_date,
                'status': attendance.status,
                'added_by': attendance.teacher.first_name + " " + attendance.teacher.last_name
            }
            for attendance in attendance_model if attendance.subject.name == subject_name
        ]
        for subject_name in {attendance.subject.name for attendance in attendance_model}
    }
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
