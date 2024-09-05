from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment,AssignmentStateEnum

from .schema import AssignmentSchema, AssignmentSubmitSchema
student_assignments_resources = Blueprint('student_assignments_resources', __name__)


@student_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    students_assignments = Assignment.get_assignments_by_student(p.student_id)
    students_assignments_dump = AssignmentSchema().dump(students_assignments, many=True)
    return APIResponse.respond(data=students_assignments_dump)


@student_assignments_resources.route('/assignments', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def upsert_assignment(p, incoming_payload):
    """Create or Edit an assignment"""
    if not incoming_payload.get('content'):
        return APIResponse.respond_with_error('Content cannot be null', 400)
    assignment = AssignmentSchema().load(incoming_payload)
    assignment.student_id = p.student_id

    upserted_assignment = Assignment.upsert(assignment)
    db.session.commit()
    upserted_assignment_dump = AssignmentSchema().dump(upserted_assignment)
    return APIResponse.respond(data=upserted_assignment_dump)


@student_assignments_resources.route('/assignments/submit', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def submit_assignment(p, incoming_payload):
    submit_assignment_payload = AssignmentSubmitSchema().load(incoming_payload)
    assignment = Assignment.get_by_id(submit_assignment_payload.id)

    # Check if the assignment is already in a submitted or graded state
    if assignment.state == AssignmentStateEnum.SUBMITTED:
        return APIResponse.respond_with_error('only a draft assignment can be submitted', 400)

    # Update the assignment to be submitted
    assignment.teacher_id = submit_assignment_payload.teacher_id
    assignment.state = AssignmentStateEnum.SUBMITTED
    db.session.commit()

    return APIResponse.respond(data=AssignmentSchema().dump(assignment))
