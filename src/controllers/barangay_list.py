from src.constants import barangay_list as brgy_list
from src.utils.api_response import ApiResponse

def barangay_list():
    try:
        return ApiResponse.success(message="Barangay List | Developer: Josuan Leonardo Hulom",payload=brgy_list)
    except Exception as e:
        return ApiResponse.error(e)