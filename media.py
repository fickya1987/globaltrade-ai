from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.user import db, User
import os
import uuid
from datetime import datetime
import mimetypes
from PIL import Image
import io

media_bp = Blueprint('media', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'm4a'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'rtf'}
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename, file_type):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return 'unknown'

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

def generate_filename(original_filename):
    """Generate unique filename"""
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    return unique_filename

def optimize_image(file_path, max_width=1920, max_height=1080, quality=85):
    """Optimize image for web"""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            
        return True
    except Exception as e:
        print(f"Image optimization error: {e}")
        return False

@media_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload media files"""
    try:
        current_user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get file type and validate
        file_type = request.form.get('type', 'auto')
        if file_type == 'auto':
            file_type = get_file_type(file.filename)
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': f'File type not allowed for {file_type}'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 50MB'}), 400
        
        # Create upload directory
        upload_path = create_upload_folder()
        
        # Generate unique filename
        filename = generate_filename(file.filename)
        file_path = os.path.join(upload_path, filename)
        
        # Save file
        file.save(file_path)
        
        # Optimize image if it's an image
        if file_type == 'image':
            optimize_image(file_path)
        
        # Get file info
        file_info = {
            'id': str(uuid.uuid4()),
            'original_name': secure_filename(file.filename),
            'filename': filename,
            'file_type': file_type,
            'file_size': file_size,
            'mime_type': mimetypes.guess_type(file.filename)[0],
            'upload_date': datetime.utcnow().isoformat(),
            'user_id': current_user_id,
            'url': f'/api/media/file/{filename}'
        }
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': file_info
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'File upload failed', 'details': str(e)}), 500

@media_bp.route('/file/<filename>', methods=['GET'])
def get_file(filename):
    """Serve uploaded files"""
    try:
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        file_path = os.path.join(upload_path, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({'error': 'File retrieval failed', 'details': str(e)}), 500

@media_bp.route('/files', methods=['GET'])
@jwt_required()
def list_user_files():
    """List user's uploaded files"""
    try:
        current_user_id = get_jwt_identity()
        
        # In a real application, you would store file metadata in database
        # For now, we'll return a mock response
        files = [
            {
                'id': '1',
                'original_name': 'sumatra_coffee.jpg',
                'filename': 'abc123.jpg',
                'file_type': 'image',
                'file_size': 2048000,
                'upload_date': '2024-01-15T10:30:00Z',
                'url': '/api/media/file/abc123.jpg'
            },
            {
                'id': '2',
                'original_name': 'product_catalog.pdf',
                'filename': 'def456.pdf',
                'file_type': 'document',
                'file_size': 5120000,
                'upload_date': '2024-01-14T15:45:00Z',
                'url': '/api/media/file/def456.pdf'
            }
        ]
        
        return jsonify({
            'files': files,
            'total': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list files', 'details': str(e)}), 500

@media_bp.route('/file/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete uploaded file"""
    try:
        current_user_id = get_jwt_identity()
        
        # In a real application, you would:
        # 1. Check if file belongs to user
        # 2. Delete from database
        # 3. Delete physical file
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'File deletion failed', 'details': str(e)}), 500

@media_bp.route('/social/share', methods=['POST'])
@jwt_required()
def share_to_social():
    """Share content to social media platforms"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['platform', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        platform = data['platform']
        content = data['content']
        media_urls = data.get('media_urls', [])
        
        # Supported platforms
        supported_platforms = ['facebook', 'twitter', 'linkedin', 'instagram', 'whatsapp']
        if platform not in supported_platforms:
            return jsonify({'error': f'Platform {platform} not supported'}), 400
        
        # Mock social media sharing
        # In a real application, you would integrate with social media APIs
        share_result = {
            'platform': platform,
            'content': content,
            'media_count': len(media_urls),
            'share_url': f'https://{platform}.com/share/abc123',
            'shared_at': datetime.utcnow().isoformat(),
            'status': 'success'
        }
        
        return jsonify({
            'message': f'Content shared to {platform} successfully',
            'share_result': share_result
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Social sharing failed', 'details': str(e)}), 500

@media_bp.route('/social/platforms', methods=['GET'])
@jwt_required()
def get_social_platforms():
    """Get available social media platforms"""
    try:
        platforms = [
            {
                'id': 'facebook',
                'name': 'Facebook',
                'icon': 'facebook',
                'description': 'Share to Facebook pages and groups',
                'supported_media': ['image', 'video'],
                'max_text_length': 63206,
                'connected': False
            },
            {
                'id': 'twitter',
                'name': 'Twitter/X',
                'icon': 'twitter',
                'description': 'Share tweets with your followers',
                'supported_media': ['image', 'video'],
                'max_text_length': 280,
                'connected': False
            },
            {
                'id': 'linkedin',
                'name': 'LinkedIn',
                'icon': 'linkedin',
                'description': 'Share professional content',
                'supported_media': ['image', 'video', 'document'],
                'max_text_length': 3000,
                'connected': False
            },
            {
                'id': 'instagram',
                'name': 'Instagram',
                'icon': 'instagram',
                'description': 'Share photos and stories',
                'supported_media': ['image', 'video'],
                'max_text_length': 2200,
                'connected': False
            },
            {
                'id': 'whatsapp',
                'name': 'WhatsApp Business',
                'icon': 'message-circle',
                'description': 'Share via WhatsApp Business',
                'supported_media': ['image', 'video', 'audio', 'document'],
                'max_text_length': 4096,
                'connected': False
            }
        ]
        
        return jsonify({
            'platforms': platforms,
            'total': len(platforms)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get social platforms', 'details': str(e)}), 500

@media_bp.route('/podcast/upload', methods=['POST'])
@jwt_required()
def upload_podcast():
    """Upload podcast/audio content"""
    try:
        current_user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        if not allowed_file(audio_file.filename, 'audio'):
            return jsonify({'error': 'Invalid audio file format'}), 400
        
        # Get metadata
        title = request.form.get('title', 'Untitled Podcast')
        description = request.form.get('description', '')
        category = request.form.get('category', 'business')
        
        # Create upload directory
        upload_path = create_upload_folder()
        
        # Generate unique filename
        filename = generate_filename(audio_file.filename)
        file_path = os.path.join(upload_path, filename)
        
        # Save audio file
        audio_file.save(file_path)
        
        # Create podcast entry
        podcast_info = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': description,
            'category': category,
            'filename': filename,
            'original_name': secure_filename(audio_file.filename),
            'file_size': os.path.getsize(file_path),
            'upload_date': datetime.utcnow().isoformat(),
            'user_id': current_user_id,
            'url': f'/api/media/file/{filename}',
            'status': 'published'
        }
        
        return jsonify({
            'message': 'Podcast uploaded successfully',
            'podcast': podcast_info
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Podcast upload failed', 'details': str(e)}), 500

@media_bp.route('/podcasts', methods=['GET'])
@jwt_required()
def list_podcasts():
    """List user's podcasts"""
    try:
        current_user_id = get_jwt_identity()
        
        # Mock podcast data
        podcasts = [
            {
                'id': '1',
                'title': 'Coffee Export Success Stories',
                'description': 'Learn how Indonesian coffee farmers are succeeding in international markets',
                'category': 'business',
                'duration': '25:30',
                'upload_date': '2024-01-15T10:30:00Z',
                'plays': 150,
                'url': '/api/media/file/podcast1.mp3'
            },
            {
                'id': '2',
                'title': 'Navigating Italian Import Regulations',
                'description': 'A guide to exporting food products to Italy',
                'category': 'education',
                'duration': '18:45',
                'upload_date': '2024-01-12T14:20:00Z',
                'plays': 89,
                'url': '/api/media/file/podcast2.mp3'
            }
        ]
        
        return jsonify({
            'podcasts': podcasts,
            'total': len(podcasts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list podcasts', 'details': str(e)}), 500

