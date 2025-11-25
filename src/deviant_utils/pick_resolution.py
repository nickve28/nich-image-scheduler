from PIL import Image

# https://www.deviantart.com/developers/console/stash/stash_publish/a799a5c0967dca14e854286df9746793
# Display resolution mapping: 0=original, 1=400px, 2=600px, 3=800px, 4=900px, 5=1024px, 6=1280px, 7=1600px, 8=1920px

DEVI_ORIGINAL_DISPLAY_RESOLUTION = 0
DISPLAY_RESOLUTIONS = [
    (1920, 8),
    (1600, 7),
    (1280, 6),
    (1024, 5),
    (900, 4),
    (800, 3),
    (600, 2),
    (400, 1),
]


def get_optimal_resolution(image_path: str) -> int:
    with Image.open(image_path) as img:
        width = img.width

    if width >= 1920:
        return 8

    # Find the largest resolution that doesn't exceed the image width
    for resolution_px, resolution_code in DISPLAY_RESOLUTIONS:
        if width >= resolution_px:
            return resolution_code

    # For images smaller than 400px, use original size
    return DEVI_ORIGINAL_DISPLAY_RESOLUTION
