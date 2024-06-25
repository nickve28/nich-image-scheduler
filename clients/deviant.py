import requests
import os

from deviant_utils.deviant_refresh_token import write_token_to_file
from deviant_utils.pick_resolution import get_optimal_resolution
from utils.account import ACCOUNT, DEVIANT_DATA

CLIENT_ID = DEVIANT_DATA['client_id']
CLIENT_SECRET = DEVIANT_DATA['client_secret']
DEVI_MATURE_CLASSIFICATION = DEVIANT_DATA.get('default_mature_classification', None)
REFRESH_TOKEN = DEVIANT_DATA['refresh_token']

def obtain_access_token():
    # Token endpoint URL
    token_url = "https://www.deviantart.com/oauth2/token"

    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN
    }
    print(data)

    response = requests.post(token_url, data=data)

    # Parse response JSON
    tokens = response.json()

    # Extract new access token
    new_access_token = tokens['access_token']
    new_refresh_token = tokens['refresh_token']
    print("Received new tokens")
    print("Access token", new_access_token)
    print("Refresh token", new_refresh_token)
    write_token_to_file(ACCOUNT, new_refresh_token)

    return new_access_token

def schedule(image_path, json_path, caption):
    try:
        access_token = obtain_access_token()
        print(f"Authenticated {access_token}")
        upload_url = "https://www.deviantart.com/api/v1/oauth2/stash/submit"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        files = {
            "file": open(image_path, "rb")
        }
        data = {
            "title": caption,
            "artist_comments": "",
            "mature_content": "false" if os.getenv('NSFW', '1') == '0' else "true",
            "is_ai_generated": "true"
        }
        response = requests.post(upload_url, headers=headers, files=files, data=data)
        json = response.json()
        print("Upload response", json)
        # {'status': 'success', 'itemid': ---, 'stack': 'Sta.sh Uploads 90', 'stackid': ---}

        submit_url = "https://www.deviantart.com/api/v1/oauth2/stash/publish"
        publish_data = {
            "itemid": json['itemid'],
            "title": caption,
            "artist_comments": "",
            "is_mature": "false" if os.getenv('NSFW', '1') == '0' else "true",
            "is_ai_generated": "true",
            "allow_free_download": "false",
            "display_resolution": get_optimal_resolution(image_path),
            # "mature_classification": DEVI_MATURE_CLASSIFICATION,
            "tags": "",
        }
        response = requests.post(submit_url, headers=headers, data=publish_data)
        submit_response = response.json()
        print("Submit response", submit_response)
        return True
    except Exception as e:
        print(f"Error while attempting to upload to Deviant: {e}")
        return False