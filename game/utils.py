# game/utils.py
import os
import requests
from io import BytesIO
from urllib.parse import urlparse
from PIL import Image, ImageFilter
from django.conf import settings


def get_blurred_poster(image_url, filter_level=3, filter_type='blur'):
    """
    Downloads a poster, applies a blur or pixel filter,
    caches it locally, and returns the media URL.
    """

    blur_strength_coefficient = 3
    min_pixel_scale = 0.25

    # Safety check
    if not image_url:
        return None

    # Calculate how strong the effect will be
    # Blur levels: 0-none, 1-low, 2-medium, 3-high...
    if filter_type == 'blur':
        blur_radius = filter_level * blur_strength_coefficient
    elif filter_type == 'pixel':
        exponent = (filter_level - 1) / 2
        pixel_scale = min_pixel_scale * ((1.0 / min_pixel_scale) ** -exponent)

    # Generate filename
    parsed_url = urlparse(image_url)
    base_filename = os.path.basename(parsed_url.path)
    if not base_filename:
        base_filename = "default_movie.jpg"

    blurred_filename = (
        f"blur_attempt_{filter_type}_lvl{filter_level}_"
        f"{base_filename}"
    )

    # Setup directories
    output_dir = os.path.join(settings.MEDIA_ROOT, 'blurred_posters')
    os.makedirs(output_dir, exist_ok=True)

    relative_save_path = os.path.join('blurred_posters', blurred_filename)
    absolute_save_path = os.path.join(settings.MEDIA_ROOT, relative_save_path)

    # Cache check
    if os.path.exists(absolute_save_path):
        return os.path.join(settings.MEDIA_URL,
                            relative_save_path).replace('\\', '/')

    # Download the image
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    # Process and save the image
    img = Image.open(BytesIO(response.content))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if filter_type == 'blur':
        if blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    elif filter_type == 'pixel':
        if pixel_scale < 1.0:
            original_size = img.size

            tiny_size = (max(1, int(original_size[0] * pixel_scale)),
                         max(1, int(original_size[1] * pixel_scale)))

            img_small = img.resize(tiny_size,
                                   resample=Image.Resampling.BILINEAR)

            img = img_small.resize(original_size,
                                   resample=Image.Resampling.NEAREST)

    img.save(absolute_save_path, "JPEG")

    return os.path.join(settings.MEDIA_URL,
                        relative_save_path).replace('\\', '/')
