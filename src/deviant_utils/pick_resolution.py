from PIL import Image


def get_optimal_resolution(image_path):
    widths = [400, 600, 800, 900, 1024, 1280, 1600, 1920]
    with Image.open(image_path) as img:
        image_width = img.width

    for i, width in enumerate(widths):
        if width >= image_width:
            return i + 1  # Add 1 because API values start at 1, not 0

    # If all widths are smaller than the image, return the highest available
    return len(widths)  # This will be 8 for 1920px
