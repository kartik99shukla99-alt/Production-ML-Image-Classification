from app.cache.redis_cache import (
    generate_image_hash,
    get_cached_prediction
)


def check_cached_prediction(image_bytes: bytes):
    """
    Generate an image hash and check Redis for
    an existing prediction.

    Returns:
        image_hash, cached_prediction
    """

    image_hash = generate_image_hash(image_bytes)

    cached_prediction = get_cached_prediction(image_hash)

    return image_hash, cached_prediction