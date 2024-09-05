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
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    
    assert response.status_code == 400








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
    assert data['error'] == 'FyleError'
    assert data['message'] == 'principal not found'


