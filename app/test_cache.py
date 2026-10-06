from app.cache.redis_cache import (
    generate_image_hash,
    cache_prediction,
)
from pathlib import Path

# Change this to your actual image path
image_path = Path("test.jpg")

image_bytes = image_path.read_bytes()

image_hash = generate_image_hash(image_bytes)

prediction = {
    "predictions": [
        {
            "class_name": "meme",
            "confidence": 0.94
        },
        {
            "class_name": "humor",
            "confidence": 0.87
        },
        {
            "class_name": "social_media",
            "confidence": 0.76
        }
    ]
}

cache_prediction(
    image_hash,
    prediction,
)

print("Image hash:")
print(image_hash)

print("\nCache populated successfully.")