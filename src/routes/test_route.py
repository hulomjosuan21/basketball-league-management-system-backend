from flask import Blueprint, jsonify, request
from src.errors.test_error import TestException, TestExceptionOne
from src.errors.errors import AuthException
from src.models.test_model import TestModel
from src.extensions import db
test_bp = Blueprint('test', __name__, url_prefix='/test')
from src.utils.api_response import ApiResponse

@test_bp.post('')
def add_test():
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return ApiResponse.error("Invalid input", 400)

        content = data.get('content')
        if not content: 
            raise AuthException("Error login")
        if content == "Hulom":
            raise TestExceptionOne("Content cannot be Hulom")
        
        new_test = TestModel(content=content)
        db.session.add(new_test)
        db.session.commit()

        tests = TestModel.query.all()
        test_list = [{"id": test.id, "content": test.content} for test in tests]

        return ApiResponse.success(message=f"{new_test.content} successfully added!", payload=test_list, status_code=201)

    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(e)

@test_bp.put('')
def update_test():
    try:
        data = request.get_json()
        new_content = data.get('content')

        test = TestModel.query.get(1)
        if test is None:
            return ApiResponse.error("Record not found"), 404

        test.content = new_content
        db.session.commit()

        return ApiResponse.success("Update successful")
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(str(e)), 500
    
@test_bp.get('')
def list_tests():
    try:
        tests = TestModel.query.all()
        test_list = [{"id": test.id, "content": test.content} for test in tests]
        
        return ApiResponse.success(payload=test_list,status_code=200)
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(e)