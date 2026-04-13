import os
import cloudinary.uploader
from django.conf import settings
from decouple import config

# Configure Cloudinary
cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET')
)

# Path to your media folder (for user-uploaded images)
media_path = os.path.join(settings.BASE_DIR, 'media')  # Adjust if different

# Also upload static images if any
static_img_path = os.path.join(settings.BASE_DIR, 'static', 'img')
signup_img_path = os.path.join(settings.BASE_DIR, 'static', 'signupimgs')

paths_to_upload = [media_path, static_img_path, signup_img_path]

for path in paths_to_upload:
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    file_path = os.path.join(root, file)
                    try:
                        result = cloudinary.uploader.upload(file_path, folder='your_folder')  # Replace 'your_folder' with desired Cloudinary folder
                        print(f"Uploaded {file}: {result['url']}")
                        # Optionally, update your database records here to point to result['url']
                    except Exception as e:
                        print(f"Failed to upload {file}: {e}")
    else:
        print(f"Path {path} does not exist.")</content>
<parameter name="filePath">/home/victoire/Desktop/My-Project/auca_project_mimic/upload_images.py