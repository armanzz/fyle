def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED','DRAFT']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json
    

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )
    print(response.json)
    assert response.status_code == 404
    data = response.json
    print(response.json)

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_get_assignments_by_teacher():
    """
    Test the get_assignments_by_teacher class method.
    """
    from core.models.assignments import Assignment

    assignments = Assignment.get_assignments_by_teacher(teacher_id=1)
    assert isinstance(assignments, list)
    for assignment in assignments:
        assert assignment.teacher_id == 1


def test_mark_grade():
    """
    Test the mark_grade method of the Assignment model.
    """
    from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
    from core.apis.decorators import AuthPrincipal
    from core import db

    # Create a submitted assignment
    assignment = Assignment(
        content='Test Content',
        student_id=1,
        teacher_id=1,
        state=AssignmentStateEnum.SUBMITTED
    )
    db.session.add(assignment)
    db.session.commit()

    auth_principal = AuthPrincipal(user_id=1, teacher_id=1)

    # Grade the assignment
    graded_assignment = Assignment.mark_grade(assignment.id, GradeEnum.A, auth_principal)

    # Refresh the assignment from the database
    db.session.refresh(assignment)

    assert assignment.grade == GradeEnum.A
    assert assignment.state == AssignmentStateEnum.GRADED
