def write_tokens_to_file(name, access_token, refresh_token):
    bash_script_content= f"""
        #!/bin/bash

        export DEVIANT_ACCESS_TOKEN={access_token}
        export DEVIANT_REFRESH_TOKEN={refresh_token}

    """
    with open(f"./refresh_token_cache/{name}.sh", "w") as file:
        file.write(bash_script_content)
