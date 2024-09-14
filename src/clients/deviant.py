import requests
import tempfile
from PIL import Image
import os

from deviant_utils.deviant_refresh_token import write_token_to_file
from utils.text_utils import remove_duplicates
from models.account import Account

TOKEN_URL = "https://www.deviantart.com/oauth2/token"
UPLOAD_URL = "https://www.deviantart.com/api/v1/oauth2/stash/submit"
SUBMIT_URL = "https://www.deviantart.com/api/v1/oauth2/stash/publish"
FOLDERS_URL = "https://www.deviantart.com/api/v1/oauth2/gallery/folders"

# https://www.deviantart.com/developers/console/stash/stash_publish/a799a5c0967dca14e854286df9746793
DEVI_ORIGINAL_DISPLAY_RESOLUTION = 0
MAX_TITLE_LENGTH = 50


def truncate_caption(caption: str):
    if len(caption) <= MAX_TITLE_LENGTH:
        return caption
    return caption[:MAX_TITLE_LENGTH]


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
            "client_secret": config.client_secret,
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

    def _strip_exif(self, image_path):
        with Image.open(image_path) as img:
            # Create a new image without EXIF data
            data = list(img.getdata())
            image_without_exif = Image.new(img.mode, img.size)
            image_without_exif.putdata(data)

            # Create a temporary file to save the stripped image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_filename = temp_file.name
                image_without_exif.save(temp_filename, "JPEG")

        return temp_filename

    def list_folders(self, username):
        access_token = self._obtain_access_token()
        print(f"Authenticated {access_token}")
        payload = {"username": username, "limit": 50}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(FOLDERS_URL, params=payload, headers=headers)
        return response.json()

    def _get_gallery_ids(self):
        config = self.account.deviant_config
        if len(config.premium_gallery_ids) > 0:
            return remove_duplicates(config.premium_gallery_ids)
        return remove_duplicates(config.gallery_ids)

    def schedule(self, image_path, caption, content_tags):
        mature_content = "false" if self.account.nsfw is False else "true"
        stripped_image_path = None
        file_handle = None
        config = self.account.deviant_config

        try:
            access_token = self._obtain_access_token()
            print(f"Authenticated {access_token}")
            upload_url = UPLOAD_URL
            headers = {"Authorization": f"Bearer {access_token}"}

            # Strip EXIF data and get the path to the temporary file
            stripped_image_path = self._strip_exif(image_path)

            file_handle = open(stripped_image_path, "rb")
            files = {"file": file_handle}
            all_tags = [tag.strip() for tag in content_tags.split(",")]
            all_tags.extend(self.account.deviant_config.tags)
            unique_tags = remove_duplicates(all_tags)
            data = {
                "title": truncate_caption(caption),
                "artist_comments": "",
                "mature_content": mature_content,
                "is_ai_generated": "true",
                "tags[]": unique_tags,
            }
            print(f"posting to {upload_url}, headers: {headers}, files: {files}, data: {data}")
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            json = response.json()
            print("Upload response", json)
            # {'status': 'success', 'itemid': ---, 'stack': 'Sta.sh Uploads 90', 'stackid': ---}
            can_be_featured = self.account.deviant_config.featured and len(config.premium_gallery_ids) == 0

            publish_data = {
                "itemid": json["itemid"],
                "title": truncate_caption(caption),
                "artist_comments": "",
                "is_mature": mature_content,
                "is_ai_generated": "true",
                "allow_free_download": "false",
                "display_resolution": DEVI_ORIGINAL_DISPLAY_RESOLUTION,
                "feature": "true" if can_be_featured else "false",
                "galleryids[]": self._get_gallery_ids(),
                # "mature_classification": DEVI_MATURE_CLASSIFICATION,
            }
            print("publish_data:", publish_data)
            response = requests.post(SUBMIT_URL, headers=headers, data=publish_data)
            submit_response = response.json()
            print("Submit response", submit_response)
            return submit_response
        except Exception as e:
            print(f"Error while attempting to upload to Deviant: {e}")
            return False
        finally:
            # Close the file handle if it's open
            if file_handle:
                file_handle.close()

            # Clean up the temporary file
            if stripped_image_path and os.path.exists(stripped_image_path):
                try:
                    os.unlink(stripped_image_path)
                    print(f"Removed temporary file: {stripped_image_path}")
                except PermissionError:
                    print(f"Unable to delete temporary file: {stripped_image_path}")
                    print("You may need to delete this file manually.")
