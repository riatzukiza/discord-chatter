"""
Small library for image processing.
"""

from PIL import Image
import base64

def get_image_bitmap(image_bytes):
    """
    Get the bitmap from a png image.
    """
    image = Image.open(image_bytes)
    return image.convert('RGB')

def base_64_encode(image_bytes):
    """
    Base 64 encode an image.
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def base_64_decode(base_64_encoded_image):
    """
    Base 64 decode an image.
    """
    return base64.b64decode(base_64_encoded_image)

def base_64_encode_bitmap(bitmap):
    """
    Base 64 encode a bitmap.
    """
    return base64.b64encode(bitmap.tobytes()).decode('utf-8')

def base_64_decode_bitmap(base_64_encoded_bitmap):
    """
    Base 64 decode a bitmap.
    """
    from PIL import Image
    image = Image.open(base64.b64decode(base_64_encoded_bitmap))
    return image.convert('RGB')
