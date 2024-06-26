import requests

from deviant_utils.deviant_refresh_token import write_token_to_file


class DeviantClient:
    def __init__(self, account_id, config):
        self.account_id = account_id
        self.config = config

    def _obtain_access_token(self):
        # Token endpoint URL
        config = self.config["id"]
        client_id = self.config["client_id"]
        client_secret = self.config["client_secret"]
        refresh_token = self.config["refresh_token"]
        token_url = "https://www.deviantart.com/oauth2/token"

        data = {"grant_type": "refresh_token", "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}
        print(data)

        response = requests.post(token_url, data=data)

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
        nsfw = self.config["nsfw"]
        mature_content = "false" if nsfw is False else True

        try:
            access_token = self._obtain_access_token()
            print(f"Authenticated {access_token}")
            upload_url = "https://www.deviantart.com/api/v1/oauth2/stash/submit"
            headers = {"Authorization": f"Bearer {access_token}"}

            files = {"file": open(image_path, "rb")}
            data = {"title": caption, "artist_comments": "", "mature_content": mature_content, "is_ai_generated": "true"}
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            json = response.json()
            print("Upload response", json)
            # {'status': 'success', 'itemid': ---, 'stack': 'Sta.sh Uploads 90', 'stackid': ---}

            submit_url = "https://www.deviantart.com/api/v1/oauth2/stash/publish"
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
            response = requests.post(submit_url, headers=headers, data=publish_data)
            submit_response = response.json()
            print("Submit response", submit_response)
            return True
        except Exception as e:
            print(f"Error while attempting to upload to Deviant: {e}")
            return False
