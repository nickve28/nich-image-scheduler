import os

def write_tokens_to_file(name, access_token, refresh_token):    
    bash_script_content= f"#!/bin/bash\nexport DEVIANT_ACCESS_TOKEN={access_token}\nexport DEVIANT_REFRESH_TOKEN={refresh_token}"
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    parent_path = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    cache_path = os.path.join(parent_path, 'refresh_token_cache')
    file_path = os.path.join(cache_path, f'{name}.sh')

    with open(file_path, "w") as file:
        file.write(bash_script_content)
