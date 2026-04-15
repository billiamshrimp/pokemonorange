import pygame

_image_cache = {}
_scaled_cache = {}


def load_image(path, convert_alpha=True):
    """
    Load an image once and reuse it.
    """
    key = (path, convert_alpha)

    if key not in _image_cache:
        image = pygame.image.load(path)
        image = image.convert_alpha() if convert_alpha else image.convert()
        _image_cache[key] = image

    return _image_cache[key]


def get_scaled_image(path, size, convert_alpha=True):
    """
    Load and scale an image once per unique size.
    """
    key = (path, size, convert_alpha)

    if key not in _scaled_cache:
        base_image = load_image(path, convert_alpha)
        _scaled_cache[key] = pygame.transform.scale(base_image, size)

    return _scaled_cache[key]


def clear_scaled_cache():
    """
    Useful if you ever change tile size or want to rebuild scaled assets.
    """
    _scaled_cache.clear()