import os
from urllib.parse import urlparse
import uuid
from src.extensions import supabase_client
from werkzeug.utils import secure_filename
from flask import current_app
from werkzeug.datastructures import FileStorage
import asyncio

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'ico'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def save_file(file: FileStorage, subfolder: str, request, storage_type: str = 'local') -> str:
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid file or unsupported file type.")
    
    original_filename = secure_filename(file.filename)
    extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    
    if storage_type.lower() == 'supabase':
        supabase = supabase_client()
        file_path = f"{subfolder}/{unique_filename}"
        
        file.seek(0)
        file_data = file.read()
        
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: supabase.storage.from_(subfolder).upload(
                file_path,
                file_data,
                file_options={'content-type': file.content_type}
            )
        )
        
        if hasattr(response, 'error') and response.error:
            raise ValueError(f"Supabase upload failed: {response.error.message}")
        
        public_url = supabase.storage.from_(subfolder).get_public_url(file_path)
        return public_url
    else:  # Default to local storage
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: file.save(file_path)
        )
        
        file_url = f"/uploads/{subfolder}/{unique_filename}"
        full_url = request.host_url.rstrip('/') + file_url
        return full_url

async def delete_file_by_url(file_url: str, storage_type: str = 'local') -> bool:
    try:
        parsed_url = urlparse(file_url)
        
        if storage_type.lower() == 'supabase':
            supabase = supabase_client()
            file_path = parsed_url.path.lstrip('/')
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: supabase.storage.from_(file_path.split('/')[0]).remove([file_path])
            )
            if hasattr(response, 'error') and response.error:
                print(f"Error deleting file from Supabase: {response.error.message}")
                return False
            return True
        else:  # Default to local storage
            file_path = parsed_url.path
            prefix = '/uploads/'
            if not file_path.startswith(prefix):
                return False
            
            relative_path = file_path[len(prefix):]
            parts = relative_path.split('/')
            if len(parts) < 2:
                return False
            
            subfolder = parts[0]
            filename = secure_filename(parts[-1])
            safe_path = os.path.join(subfolder, filename)
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_path)
            
            if os.path.exists(full_path):
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: os.remove(full_path)
                )
                return True
            
            return False
    except Exception as e:
        print(f"Error deleting file by URL: {e}")
        return False