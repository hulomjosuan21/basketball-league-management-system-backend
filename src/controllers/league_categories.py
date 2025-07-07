from src.constants import league_categories_list
from src.utils.api_response import ApiResponse

def league_categories():
    try:
        return ApiResponse.success(message="League Categories | Developer: Josuan Leonardo Hulom",payload=league_categories_list)
    except Exception as e:
        return ApiResponse.error(e)