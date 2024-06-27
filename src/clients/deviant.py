import requests

from deviant_utils.deviant_refresh_token import write_token_to_file
from models.account import Account

TOKEN_URL = "https://www.deviantart.com/oauth2/token"
UPLOAD_URL = "https://www.deviantart.com/api/v1/oauth2/stash/submit"
SUBMIT_URL = "https://www.deviantart.com/api/v1/oauth2/stash/publish"


class DeviantClient:
    account: Account

    def __init__(self, account: Account):
        if not account.deviant_config:
            raise RuntimeError("No Deviant config found")

        self.account = account

    def _obtain_access_token(self):
        # Token endpoint URL
        config = self.account.deviant_config

        data = {
            "grant_type": "refresh_token",
            "client_id": config.client_id,
            "client_secret": config.client_id,
            "refresh_token": config.refresh_token,
        }
        print(data)

        response = requests.post(TOKEN_URL, data=data)

        # Parse response JSON
        tokens = response.json()
        print("Debug token response", tokens)

        # Extract new access token
        new_access_token = tokens["access_token"]
        new_refresh_token = tokens["refresh_token"]
        print("Received new tokens")
        print("Access token", new_access_token)
        print("Refresh token", new_refresh_token)
        write_token_to_file(self.account.id, new_refresh_token)

        return new_access_token

    def schedule(self, image_path, caption):
        mature_content = "false" if self.account.nsfw is False else "true"

        try:
            access_token = self._obtain_access_token()
            print(f"Authenticated {access_token}")
            upload_url = UPLOAD_URL
            headers = {"Authorization": f"Bearer {access_token}"}

            files = {"file": open(image_path, "rb")}
            data = {"title": caption, "artist_comments": "", "mature_content": mature_content, "is_ai_generated": "true"}
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            json = response.json()
            print("Upload response", json)
            # {'status': 'success', 'itemid': ---, 'stack': 'Sta.sh Uploads 90', 'stackid': ---}

            publish_data = {
                "itemid": json["itemid"],
                "title": caption,
                "artist_comments": "",
                "is_mature": mature_content,
                "is_ai_generated": "true",
                "allow_free_download": "false",
                # "display_resolution": get_optimal_resolution(image_path),
                # "mature_classification": DEVI_MATURE_CLASSIFICATION,
                "tags": "",
            }
            response = requests.post(SUBMIT_URL, headers=headers, data=publish_data)
            submit_response = response.json()
            print("Submit response", submit_response)
            return True
        except Exception as e:
            print(f"Error while attempting to upload to Deviant: {e}")
            return False
