import os


def get_refresh_token(name):
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    parent_path = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    cache_path = os.path.join(parent_path, "refresh_token_cache")
    file_path = os.path.join(cache_path, name)

    return open(file_path, "r").read()


def write_token_to_file(name, refresh_token):
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    parent_path = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    cache_path = os.path.join(parent_path, "refresh_token_cache")
    file_path = os.path.join(cache_path, name)
    breakpoint()

    with open(file_path, "w") as file:
        file.write(refresh_token)
