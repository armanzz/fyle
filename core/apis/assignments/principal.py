from flask import Blueprint
from core.models.teachers import Teacher
from core.apis.responses import APIResponse
from core.apis.decorators import authenticate_principal  # Import the correct decorator
# Import the app from the core module (or wherever it's defined)
from core import app

from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core.libs.assertions import assert_found
from core import db

from core.apis.decorators import accept_payload
from .schema import AssignmentSchema, AssignmentGradeSchema


principal_resources = Blueprint('principal_resources', __name__)

@principal_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@authenticate_principal  # Use the correct decorator
def get_teachers(principal):
    """Get all teachers"""
    teachers = Teacher.query.all()
    teachers_dump = [{'id': teacher.id, 'user_id': teacher.user_id, 'created_at': teacher.created_at, 'updated_at': teacher.updated_at} for teacher in teachers]
    return APIResponse.respond(data=teachers_dump)

@principal_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@authenticate_principal  # Use the correct decorator
def get_assignments(principal):
    """Get all submitted and graded assignments"""
    assignments = Assignment.query.filter(Assignment.state.in_([AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])).all()
    assignments_dump = [{'id': assignment.id, 'content': assignment.content, 'student_id': assignment.student_id, 'teacher_id': assignment.teacher_id, 'state': assignment.state, 'created_at': assignment.created_at, 'updated_at': assignment.updated_at} for assignment in assignments]
    return APIResponse.respond(data=assignments_dump)

@principal_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@authenticate_principal
@accept_payload
def grade_assignment(principal, incoming_payload):
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    
    
    assignment = Assignment.get_by_id(grade_assignment_payload.id)
    
    assert_found(assignment, 'No assignment with this id was found')

    
    assignment.grade = grade_assignment_payload.grade
    assignment.state = AssignmentStateEnum.GRADED
    db.session.commit()

    return APIResponse.respond(data=AssignmentSchema().dump(assignment))
