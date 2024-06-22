import os
import glob
from dotenv import load_dotenv
import tkinter as tk
from PIL import Image, ImageTk

load_dotenv()

directory_path = os.getenv('DIRECTORY_PATH')
extensions = os.getenv('EXTENSIONS').split(',')

def find_images_in_folder(folder_path):
    image_paths = []
    for ext in extensions:
        print(os.path.join(folder_path, f'*{ext}'))
        image_paths.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
    return image_paths


def display_image_with_input(image_path):
    # Create a Tkinter window
    window = tk.Tk()
    window.title("Image Window")

    # Load the image using PIL
    image = Image.open(image_path)
    
    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the aspect ratio
    image_width, image_height = image.size
    aspect_ratio = image_width / image_height

    # Calculate the window size to maintain aspect ratio and fit within screen
    new_width = int(screen_width * 0.75)
    new_height = int(screen_height * 0.75)

    if aspect_ratio > 1:  # Width is greater than height
        new_height = int(new_width / aspect_ratio)
    else:  # Height is greater than width
        new_width = int(new_height * aspect_ratio)

    # Resize the image to fit within the calculated size
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    # Set the window size to the screen size
    window.geometry(f"{screen_width}x{screen_height}")

    # Create a Label widget to display the image and center it
    label = tk.Label(window, image=photo)
    label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    # Create an Entry widget for user input below the image
    input_field = tk.Entry(window)
    input_field.place(relx=0.5, rely=0.8, anchor=tk.CENTER, width=screen_width * 0.5)  # Centered and 50% of screen width

    # Function to handle user input
    def handle_input():
        user_input = input_field.get()
        print(f"User Input: {user_input}")

    # Button to submit the input
    submit_button = tk.Button(window, text="Submit", command=handle_input)
    submit_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)  # Centered below the input field

    # Start the Tkinter main loop
    window.mainloop()

if __name__ == "__main__":
    for image_path in find_images_in_folder(directory_path):
        display_image_with_input(image_path)