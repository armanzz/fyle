from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment,AssignmentStateEnum

from .schema import AssignmentSchema, AssignmentGradeSchema
teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(grade_assignment_payload.id)

    if assignment is None:
        return APIResponse.respond_with_error('No assignment with this id was found', 404)


    if assignment.teacher_id != p.teacher_id:
        return APIResponse.respond_with_error('You are not authorized to grade this assignment', 400)

    assignment.grade = grade_assignment_payload.grade
    assignment.state = AssignmentStateEnum.GRADED
    db.session.commit()

    return APIResponse.respond(data=AssignmentSchema().dump(assignment))
