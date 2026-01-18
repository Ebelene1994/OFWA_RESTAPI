import asyncio
from typing import Any, Dict

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError
from fastapi import UploadFile

class CloudinaryService:
    @staticmethod
    def upload_file(file: UploadFile, folder: str = "ofwa_dash") -> dict:
        try:
            # Ensure stream is at beginning
            try:
                file.file.seek(0)
            except Exception:
                pass

            result = cloudinary.uploader.upload(
                file.file,
                folder=folder,
                resource_type="raw",
                use_filename=True,
                unique_filename=True,
                overwrite=False,
            )

            secure_url = result.get("secure_url") or (
                result.get("url").replace("http://", "https://") if result.get("url") else None
            )
            if secure_url:
                # Maintain backward compatibility while ensuring secure URL usage
                result["secure_url"] = secure_url
                result["url"] = secure_url

            return result
        except CloudinaryError as e:
            raise RuntimeError(f"Cloudinary upload failed: {e}") from e
        except Exception as e:
            raise e

    @staticmethod
    def delete_file(public_id: str):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result
        except Exception as e:
            raise e

    @staticmethod
    async def upload_file_async(file: UploadFile, folder: str = "ofwa_dash") -> Dict[str, Any]:
        try:
            # Read file content asynchronously to avoid blocking
            content = await file.read()
            # Reset pointer for potential downstream consumers
            try:
                file.file.seek(0)
            except Exception:
                pass

            loop = asyncio.get_running_loop()

            def _upload():
                return cloudinary.uploader.upload(
                    content,
                    folder=folder,
                    resource_type="raw",
                    use_filename=True,
                    unique_filename=True,
                    overwrite=False,
                    filename=file.filename,
                )

            result = await loop.run_in_executor(None, _upload)

            secure_url = result.get("secure_url") or (
                result.get("url").replace("http://", "https://") if result.get("url") else None
            )
            if secure_url:
                result["secure_url"] = secure_url
                result["url"] = secure_url

            return result
        except CloudinaryError as e:
            raise RuntimeError(f"Cloudinary upload failed: {e}") from e
        except Exception as e:
            raise e
