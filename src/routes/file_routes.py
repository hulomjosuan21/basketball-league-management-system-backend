from flask import Blueprint, request, jsonify
from src.utils.file_utils import save_file, delete_file_by_url

class FileRoutes:
    def __init__(self, app):
        self.bp = Blueprint('file_routes', __name__, url_prefix="/uploads")

        @self.bp.post('')
        def upload_file():
            print("REQUEST: ",request)
            if 'file' not in request.files:
                return jsonify({'error': 'No file part in request'}), 400
            
            file = request.files['file']
            try:
                full_url = save_file(file, 'images', request)
                return jsonify({'message': 'File uploaded successfully', 'url': full_url}), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            
        @self.bp.delete('')
        def delete_file_route():
            data = request.json
            file_url = data.get('url')
            if not file_url:
                return jsonify({'error': 'File URL required'}), 400

            success = delete_file_by_url(file_url,'supabase')
            if success:
                return jsonify({'message': 'File deleted successfully'}), 200
            else:
                return jsonify({'error': 'File not found or could not be deleted'}), 404

    def get_blueprint(self):
        return self.bp
