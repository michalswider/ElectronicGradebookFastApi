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
        for subject_name in { attendance.subject.name for attendance in attendance_model}
    }
    return student_attendance