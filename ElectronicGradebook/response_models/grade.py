def map_grades_to_response(grades):
    grouped_grades = {
        subject_name: [
            {
                'id': grade.id,
                'grade': grade.grade,
                'date': grade.date,
                'added_by': f"{grade.teacher.first_name} {grade.teacher.last_name}"
            }
            for grade in grades if grade.subject.name == subject_name
        ]
        for subject_name in {grade.subject.name for grade in grades}
    }
    return grouped_grades

def map_grades_to_students_response(grades):
    result = {}
    for grade in grades:
        student_name = f"{grade.student.first_name} {grade.student.last_name}"
        if student_name not in result:
            result[student_name] = []

        result[student_name].append({
            'id': grade.id,
            'grade': grade.grade,
            'date': grade.date,
            'added_by': f"{grade.teacher.first_name} {grade.teacher.last_name}",
        })
    return result

def map_average_grades_by_class_response(class_model, average):
    return {
        'class': class_model,
        'average_grade': average
    }