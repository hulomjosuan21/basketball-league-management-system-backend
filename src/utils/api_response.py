from flask import jsonify, make_response
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from werkzeug.exceptions import NotFound, Forbidden
from src.errors.test_error import TestException
from src.errors.errors import AuthException

class ApiResponse:
    @staticmethod
    def success(redirect=None,message="Success", payload=None, status_code=200):
        response = {
            "status": True,
            "message": message,
        }
        if payload is not None:
            response["payload"] = payload
        if redirect is not None:
            response["redirect"] = redirect
            
        return make_response(jsonify(response), status_code)
    
    @staticmethod
    def html(template=None, status_code=200):
        return make_response(template, status_code)

    @staticmethod
    def error(error="An error occurred", status_code=None):
        message = "An error occurred"
        code = 500

        if isinstance(error, Exception):
            if isinstance(error, IntegrityError):
                message = "Duplicate entry or constraint violation"
                code = 409
            elif isinstance(error, DataError):
                message = "Invalid data format or length"
                code = 400
            elif isinstance(error, NotFound):
                message = "Resource not found"
                code = 404
            elif isinstance(error, AuthException):
                message = getattr(error, 'message', str(error))
                code = getattr(error, 'status_code', 401)
            elif isinstance(error, ValueError):
                message = error.message if hasattr(error, 'message') else str(error)
                code = 401
            elif isinstance(error, OperationalError):
                message = "Database operational error"
                code = 503
            elif isinstance(error, TestException):
                message = error.message if hasattr(error, 'message') else str(error)
                code = 400
            else:
                message = str(error) or message
        else:
            message = error

        if status_code is not None:
            code = status_code

        response = {
            "status": False,
            "message": message
        }
        return make_response(jsonify(response), code)
