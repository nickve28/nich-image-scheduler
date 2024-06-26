import requests

from deviant_utils.deviant_refresh_token import write_token_to_file

TOKEN_URL = "https://www.deviantart.com/oauth2/token"
UPLOAD_URL = "https://www.deviantart.com/api/v1/oauth2/stash/submit"
SUBMIT_URL = "https://www.deviantart.com/api/v1/oauth2/stash/publish"


class DeviantClient:
    def __init__(self, account_id, config):
        self.account_id = account_id
        self.config = config

    def _obtain_access_token(self):
        # Token endpoint URL
        client_id = self.config["client_id"]
        client_secret = self.config["client_secret"]
        refresh_token = self.config["refresh_token"]

        data = {"grant_type": "refresh_token", "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}
        print(data)

        response = requests.post(TOKEN_URL, data=data)

        # Parse response JSON
        tokens = response.json()

        # Extract new access token
        new_access_token = tokens["access_token"]
        new_refresh_token = tokens["refresh_token"]
        print("Received new tokens")
        print("Access token", new_access_token)
        print("Refresh token", new_refresh_token)
        write_token_to_file(self.account_id, new_refresh_token)

        return new_access_token

    def schedule(self, image_path, caption):
        nsfw = self.config.get("nsfw", False)
        mature_content = "false" if nsfw is False else "true"

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
