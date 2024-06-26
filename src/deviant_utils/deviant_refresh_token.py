import os


def get_refresh_token(name):
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    parent_path = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    project_root = os.path.join(parent_path, "..")
    cache_path = os.path.join(project_root, "refresh_token_cache")
    file_path = os.path.join(cache_path, name)

    if os.path.exists(file_path):
        return open(file_path, "r").read().replace("\n", "")  # in case of manual interference
    return None


def write_token_to_file(name, refresh_token):
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    parent_path = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    project_root = os.path.join(parent_path, "..")
    cache_path = os.path.join(project_root, "refresh_token_cache")
    file_path = os.path.join(cache_path, name)

    with open(file_path, "w") as file:
        file.write(refresh_token)
