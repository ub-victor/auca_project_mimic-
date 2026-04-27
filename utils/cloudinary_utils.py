import cloudinary
import cloudinary.uploader
from decouple import config


def configure_cloudinary():
    cloudinary.config(
        cloud_name=config('CLOUDINARY_CLOUD_NAME', default='placeholder'),
        api_key=config('CLOUDINARY_API_KEY', default='placeholder'),
        api_secret=config('CLOUDINARY_API_SECRET', default='placeholder'),
    )


def upload_file(file_path, folder='uploads'):
    configure_cloudinary()
    return cloudinary.uploader.upload(str(file_path), folder=folder)
