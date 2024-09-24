from core.models.assignments import AssignmentStateEnum, GradeEnum
from core.models.assignments import Assignment


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    Failure case: If an assignment is in DRAFT state, it cannot be graded by the principal.
    """
    from core.models.assignments import Assignment, AssignmentStateEnum
    from core import db

    # Create an assignment that is in the DRAFT state
    draft_assignment = Assignment(
        content='Test Content',
        student_id=1,
        teacher_id=1,
        state=AssignmentStateEnum.DRAFT  # Ensure it is in DRAFT state
    )
    db.session.add(draft_assignment)
    db.session.commit()

    # Attempt to grade the draft assignment
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': draft_assignment.id,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    # Check that grading a draft assignment is not allowed
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'
    assert data['message'] == 'Cannot grade assignment in current state'



def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.C.name
        },
        headers=h_principal
    )
    print(response.json)
    assert response.status_code == 200
    data = response.json
   
    

    


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    





def test_grade_assignment_unauthorized(client):
    """
    Failure case: Attempt to grade assignment without authentication
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.A.value
        }
    )
    
    assert response.status_code == 401
    data = response.json
    



def test_authenticate_principal_invalid_header_format(client):
    """
    Test that an invalid JSON in X-Principal header returns a 400 error.
    """
    response = client.get(
        '/principal/teachers',
        headers={'X-Principal': 'invalid_json'}
    )

    assert response.status_code == 400
    data = response.json
   


def test_assignment_submit_method(client):
    """
    Test the submit method of the Assignment model.
    """
    from core.models.assignments import Assignment, AssignmentStateEnum
    from core.apis.decorators import AuthPrincipal
    from core import db

    # Create a draft assignment
    assignment = Assignment(
        content='Test Content',
        student_id=1,
        state=AssignmentStateEnum.DRAFT
    )
    db.session.add(assignment)
    db.session.commit()

    auth_principal = AuthPrincipal(user_id=1, student_id=1)

    # Submit the assignment
    submitted_assignment = Assignment.submit(assignment.id, teacher_id=1, auth_principal=auth_principal)

    # Refresh the assignment from the database
    db.session.refresh(assignment)

    assert assignment.teacher_id == 1
    assert assignment.state == AssignmentStateEnum.SUBMITTED


