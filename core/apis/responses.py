from flask import Response, jsonify, make_response


class APIResponse(Response):
    @classmethod
    def respond(cls, data):
        return make_response(jsonify(data=data))
    @staticmethod
    def respond_with_error(message, status_code):
        response = {"error": "FyleError", "message": message}
        return response, status_code
