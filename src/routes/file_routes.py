import asyncio
from flask import Blueprint, request
from src.utils.api_response import ApiResponse

file_bp = Blueprint('file', __name__, url_prefix='/file')

from src.services.cloudinary_service import CloudinaryService

@file_bp.delete('/delete')
async def delete_file():
    file_url = request.args.get("url")
    if not file_url:
        return {"error": "Missing URL"}, 400

    try:
        await CloudinaryService.delete_file_by_url(file_url)
        return ApiResponse.success(message="delete")
    except Exception as e:
        return ApiResponse.error(e)
