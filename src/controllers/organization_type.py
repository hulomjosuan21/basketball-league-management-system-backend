from src.constants import organization_type_list as ls
from src.utils.api_response import ApiResponse

def organization_type_list():
    try:
        return ApiResponse.success(message="Organization Types | Developer: Josuan Leonardo Hulom",payload=ls)
    except Exception as e:
        return ApiResponse.error(e)