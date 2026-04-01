"""
Նկարների մշակման օգնական ֆունկցիաներ
"""
import os
from PIL import Image
from werkzeug.utils import secure_filename
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = os.path.join('static', 'uploads')
THUMBNAIL_SIZE = (300, 300)

def allowed_file(filename):
    """Ստուգել՝ արդյոք ֆայլի ձևաչափը թույլատրված է"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Ստեղծել ունիկալ ֆայլի անուն"""
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4()}.{ext}"

def create_thumbnail(image_path):
    """Ստեղծել նկարի փոքր տարբերակը (cross-platform)."""
    folder = os.path.dirname(image_path)
    base = os.path.basename(image_path)
    thumbnail_name = f"thumb_{base}"
    thumbnail_path = os.path.join(folder, thumbnail_name)
    with Image.open(image_path) as img:
        img.thumbnail(THUMBNAIL_SIZE)
        img.save(thumbnail_path)
    return thumbnail_path

def save_image(file, folder=UPLOAD_FOLDER):
    """Պահպանել նկարը և ստեղծել փոքր տարբերակը"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        
        # Ստեղծել պանակը, եթե այն գոյություն չունի
        os.makedirs(folder, exist_ok=True)
        
        # Պահպանել հիմնական նկարը
        file_path = os.path.join(folder, unique_filename)
        file.save(file_path)
        
        # Ստեղծել և պահպանել փոքր տարբերակը
        thumbnail_path = create_thumbnail(file_path)
        
        return {
            'filename': unique_filename,
            'original_path': file_path,
            'thumbnail_path': thumbnail_path
        }
    return None

def delete_image(filename, folder=UPLOAD_FOLDER):
    """Ջնջել նկարը և իր փոքր տարբերակը"""
    if filename:
        file_path = os.path.join(folder, filename)
        thumbnail_path = os.path.join(folder, f"thumb_{filename}")
        
        # Ջնջել ֆայլերը, եթե դրանք գոյություն ունեն
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
