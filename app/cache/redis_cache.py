import hashlib
import json
import redis
from io import BytesIO
from PIL import Image
from app.config import settings

#Redis connection
redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses = True
)

def generate_image_hash(image_bytes: bytes) -> str:
    image = Image.open(BytesIO(image_bytes))
    image = image.convert("RGB") #convert into color
    image = image.resize((224,224))
    buffer = BytesIO()
    image.save(
        buffer,
        format="JPEG",
        quality=95,
        optimize=False,
        progressive = False,
    )
    canonical_bytes = buffer.getvalue()
    return hashlib.sha256(canonical_bytes).hexdigest()

def generate_cache_key(image_hash: str):

    return f"prediction:{settings.model_version}:{image_hash}"

def get_cached_prediction(image_hash: str):

    cache_key = generate_cache_key(image_hash)
    cache_data = redis_client.get(cache_key)
    if cache_data is None :
        return None

    return json.loads(cache_data)

def cache_prediction(image_hash: str, prediction:dict)-> None:

    cache_key = generate_cache_key(image_hash)
    redis_client.setex(
        cache_key,
        settings.cache_ttl_seconds,
        json.dumps(prediction)
    )

def delete_cached_prediction(image_hash : str) -> None:
    cache_key = generate_cache_key(image_hash)
    redis_client.delete(cache_key)

def redis_health_check() ->bool:
    try :
        return redis_client.ping()
    except redis.RedisError:
        return False




    
