from pathlib import Path

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

def save_image(
    task_id: str,
    image_bytes: bytes,
) -> str:
    
    #Save image temporarily and return its path.

    file_path = UPLOAD_DIR / f"{task_id}.jpg"
    file_path.write_bytes(image_bytes)
    return str(file_path)

def delete_image(file_path: str) -> None:
    
    #Delete temporary image after processing.

    path = Path(file_path)
    if path.exists():
        path.unlink()