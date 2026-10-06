from io import BytesIO
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError
from app.config import settings

class ImageValidationError(Exception):
    pass
async def validate_image(file: UploadFile) ->bytes:
    if not file:
        raise ImageValidationError("No Image File is provided: ")

    if file.content_type not in settings.allowed_image_type_list:
        raise ImageValidationError(f"Unsupported image type: {file.content_type}." 
                                   f"Allowed type: {settings.allowed_image_type_list}")
    image_bytes = await file.read()
    if len (image_bytes)> settings.max_image_size_bytes:
        raise ImageValidationError(f"Image exceeds max size of: {settings.max_image_size_mb}Mb.")
    if len (image_bytes)==0:
        raise ImageValidationError(f"Uploaded Image is Empty.")
    try: 
        image =Image.open(BytesIO(image_bytes))
        image.verify()
    except (UnidentifiedImageError,OSError):
        raise ImageValidationError(
            "Uploades file is not a valid image."
        )
    return image_bytes
