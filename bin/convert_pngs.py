import os
import sys
import piexif
import piexif.helper
from PIL import Image, ExifTags
from colorama import init, Fore

init(autoreset=True)  # Automatically resets colors back to normal after printing


def print_red(message):
    print(Fore.RED + message)


def print_green(message):
    print(Fore.GREEN + message)


def extract_metadata(png_path, key):
    with Image.open(png_path) as img:
        if img.format != "PNG":
            return None
        return img.info.get(key)


def convert_to_jpg(png_path, metadata=None):
    with Image.open(png_path) as img:
        # Ensure RGB mode (JPEG doesn't support alpha channel like PNG)
        if img.mode not in ("RGB", "L"):  # L is for grayscale images
            img = img.convert("RGB")
        jpg_filename = os.path.splitext(png_path)[0] + ".jpg"
        img.save(jpg_filename, format="JPEG", quality=90)
        print(f"  Converting to JPG: {jpg_filename}.")
        if metadata:
            exif_bytes = piexif.dump(
                {
                    "Exif": {piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(metadata, encoding="unicode")},
                }
            )
            piexif.insert(exif_bytes, jpg_filename)


if len(sys.argv) < 2:
    print_red("Please provide a base directory as a command-line parameter.")
    sys.exit(1)

base_directory = sys.argv[1]

if not os.path.exists(base_directory):
    print_red(f"Error: The directory '{base_directory}' does not exist.")
    sys.exit(1)
elif not os.path.isdir(base_directory):
    print_red(f"Error: '{base_directory}' is not a directory.")
    sys.exit(1)

for root, dirs, files in os.walk(base_directory):
    for file in files:
        if file.endswith(".png"):
            full_path = os.path.join(root, file)

            print(f"Checking: {full_path}")
            # Check if file already exists
            jpg_filename = os.path.splitext(full_path)[0] + ".jpg"
            if os.path.exists(jpg_filename):
                print_green(f"  Skipped: {jpg_filename} already exists.")
                continue

            comfy_value = extract_metadata(full_path, "workflow")
            a1111_value = extract_metadata(full_path, "parameters")

            if comfy_value:
                json_filename = os.path.splitext(full_path)[0] + ".json"
                print(f"  Writing ComfyUI workflow: {json_filename}")

                try:
                    with open(json_filename, "w") as json_file:
                        json_file.write(comfy_value)
                except UnicodeEncodeError as e:
                    print_red(f"  Warning: Failed to write {json_filename} due to encoding issues: {e}")
                    continue

            if comfy_value or a1111_value:
                convert_to_jpg(full_path, a1111_value)
                os.remove(full_path)
            else:
                print_green(f"  Skipped: {full_path} (no 'workflow' or 'parameters' keys or is not a valid PNG)")
