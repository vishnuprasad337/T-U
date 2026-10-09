# utils/image_optimizer.py
import io
import os

from django.core.cache import cache
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

# Widths generated for every uploaded image. The largest one is the main file.
WIDTHS = (480, 800, 1200)
MAIN_WIDTH = max(WIDTHS)


# ---------------------------------------------------------------------------
# NEW: in-memory optimization (works with Supabase / S3 remote storage)
# ---------------------------------------------------------------------------
def _encode(img, width, quality):
    """Resize (never upscale) and encode as WebP."""
    img = img.copy()
    if img.width > width:
        ratio = width / img.width
        img = img.resize((width, round(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    return ContentFile(buf.getvalue())


def build_variants(file, widths=WIDTHS, quality=70):
    """Return {width: ContentFile} of WebP images, built fully in memory."""
    file.seek(0)
    with Image.open(file) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.load()
    return {w: _encode(img, w, quality) for w in widths}


def variant_name(name, width):
    """'activities/game.webp' -> 'activities/game-480.webp'"""
    stem = os.path.splitext(name)[0]
    return f"{stem}-{width}.webp"


def srcset_for(fieldfile):
    """Build a srcset string, but only if the resized variants exist.
    Old images without variants return "" so the browser uses plain src."""
    if not fieldfile:
        return ""

    name = fieldfile.name
    cache_key = f"srcset_ok:{name}"
    ok = cache.get(cache_key)

    if ok is None:
        try:
            storage = fieldfile.storage
            ok = name.endswith(".webp") and all(
                storage.exists(variant_name(name, w))
                for w in WIDTHS
                if w != MAIN_WIDTH
            )
        except Exception:
            ok = False
        # cache "yes" for a day, "no" for 10 minutes so a re-upload shows up quickly
        cache.set(cache_key, ok, 86400 if ok else 600)

    if not ok:
        return ""

    storage = fieldfile.storage
    parts = [
        f"{storage.url(variant_name(name, w))} {w}w"
        for w in WIDTHS
        if w != MAIN_WIDTH
    ]
    parts.append(f"{fieldfile.url} {MAIN_WIDTH}w")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# KEPT: old local-file helpers (only work with local filesystem paths)
# ---------------------------------------------------------------------------
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