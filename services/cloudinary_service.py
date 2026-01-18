import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile

class CloudinaryService:
    @staticmethod
    def upload_file(file: UploadFile, folder: str = "ofwa_dash") -> dict:
        try:
            result = cloudinary.uploader.upload(
                file.file,
                folder=folder,
                resource_type="auto"
            )
            return result
        except Exception as e:
            raise e

    @staticmethod
    def delete_file(public_id: str):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result
        except Exception as e:
            raise e
