import json
from flask import request, jsonify
from core.libs import assertions
from functools import wraps


class AuthPrincipal:
    def __init__(self, user_id, student_id=None, teacher_id=None, principal_id=None):
        self.user_id = user_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.principal_id = principal_id


def accept_payload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        incoming_payload = request.json
        return func(incoming_payload, *args, **kwargs)
    return wrapper


def authenticate_principal(func):
    @wraps(func)  # Ensure to preserve the original function's metadata
    def wrapper(*args, **kwargs):
        p_str = request.headers.get('X-Principal')

        # Ensure the principal header exists
        assertions.assert_auth(p_str is not None, 'principal not found')

        try:
            p_dict = json.loads(p_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid principal header format', 'message': 'X-Principal header must be a valid JSON string'}), 400
        
        # Ensure required fields in principal header
        assertions.assert_auth('user_id' in p_dict, 'user_id is missing in principal header')
        p = AuthPrincipal(
            user_id=p_dict['user_id'],
            student_id=p_dict.get('student_id'),
            teacher_id=p_dict.get('teacher_id'),
            principal_id=p_dict.get('principal_id')
        )

        # Validate requester role based on the URL path
        if request.path.startswith('/student'):
            assertions.assert_true(p.student_id is not None, 'requester should be a student')
        elif request.path.startswith('/teacher'):
            assertions.assert_true(p.teacher_id is not None, 'requester should be a teacher')
        elif request.path.startswith('/principal'):
            assertions.assert_true(p.principal_id is not None, 'requester should be a principal')
        else:
            assertions.assert_found(None, 'No such API path found')

        return func(p, *args, **kwargs)  # Make sure you pass 'p' as a keyword argument
    return wrapper
