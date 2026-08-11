# utils/image_optimizer.py
from PIL import Image
import os


def optimize_image(image_path, max_width=1200, max_height=1200, quality=75):
    """
    Resize + compress images to reduce file size without losing much quality.
    """
    if not os.path.exists(image_path):
        return
    original_size = os.path.getsize(image_path) / 1024  # in KB

    with Image.open(image_path) as img:
        img = img.convert("RGB")  # ensure JPEG compatibility

        # Resize only if image is larger than limits
        img.thumbnail((max_width, max_height), Image.LANCZOS)

        # Save optimized (overwrite original)
        img.save(image_path, optimize=True, quality=quality)

    new_size = os.path.getsize(image_path) / 1024  # in KB
    print(
        f"[OPTIMIZER] {os.path.basename(image_path)} optimized: {original_size:.1f} KB → {new_size:.1f} KB"
    )


def optimize_flag(image_path, size=(40, 40), quality=85):
    """
    Special optimization for country flags (fixed small size).
    """
    if not os.path.exists(image_path):
        return

    original_size = os.path.getsize(image_path) / 1024

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        img.save(image_path, optimize=True, quality=quality)

    new_size = os.path.getsize(image_path) / 1024
    print(
        f"[OPTIMIZER] Flag {os.path.basename(image_path)} resized to {size} and optimized: {original_size:.1f} KB → {new_size:.1f} KB"
    )
