from flask import request, jsonify
from src.services.cloudinary_service import CloudinaryService
from src.utils.api_response import ApiResponse
from werkzeug.datastructures import FileStorage
from typing import Type
import asyncio
from src.extensions import db
from flask_sqlalchemy.model import Model

def update_model_image(
    model: Type[Model],
    record_id: str,
    id_field: str,
    image_field: str,
    folder: str = "uploads"
):
    file: FileStorage = request.files.get("file")

    if not file:
        raise ValueError("No file provided")

    record = db.session.query(model).filter(getattr(model, id_field) == record_id).first()

    if not record:
        raise ValueError(f"{model.__name__} not found")

    try:
        new_url = asyncio.run(CloudinaryService.upload_file(file, folder=folder))

        old_url = getattr(record, image_field, None)
        if old_url:
            asyncio.run(CloudinaryService.delete_file_by_url(old_url))

        setattr(record, image_field, new_url)
        db.session.commit()

        return ApiResponse.success(message=f"{model.__name__} {image_field} updated successfully.",payload=new_url)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
