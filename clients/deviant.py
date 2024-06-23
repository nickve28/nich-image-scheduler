import requests
import os

from dotenv import load_dotenv

load_dotenv(
    '.env',
    None,
    False,
    True
)

ID = os.getenv('ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
DEVI_MATURE_CLASSIFICATION = os.getenv('DEVI_MATURE_CLASSIFICATION')
ACCESS_TOKEN = os.getenv(f'{ID}_ACCESS_TOKEN')

def schedule(image_path, json_path, caption):
    print(f"Authenticated {ACCESS_TOKEN}")
    upload_url = "https://www.deviantart.com/api/v1/oauth2/stash/submit"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    files = {
        "file": open(image_path, "rb")
    }
    data = {
        "title": caption,
        "artist_comments": "",
        "mature_content": "false" if os.getenv('NSFW') == 0 else "true",
        "ai_content": "true"
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
        "is_mature": "false" if os.getenv('NSFW') == 0 else "true",
        "is_ai_generated": "true",
        "mature_classification": DEVI_MATURE_CLASSIFICATION,
        "tags": "",
    }
    # response = requests.post(submit_url, headers=headers, data=publish_data)
    # submit_response = response.json()
    # print("Submit response", submit_response)
    return json