
import requests
from dotenv import load_dotenv
import os

load_dotenv(
    '.env',
    None,
    False,
    True
)

ID = os.getenv('ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv(f'{ID}_REFRESH_TOKEN')

# Token endpoint URL
token_url = "https://www.deviantart.com/oauth2/token"

data = {
    'grant_type': 'refresh_token',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': REFRESH_TOKEN
}

response = requests.post(token_url, data=data)

# Parse response JSON
tokens = response.json()

# Extract new access token
new_access_token = tokens['access_token']
new_refresh_token = tokens['refresh_token']
print('Access token', new_access_token)
print('Refresh token', new_refresh_token)

# todo this isn't setting it in the bash session now. maybe we should write to a file instead?
os.environ['{ID}_ACCESS_TOKEN'] = new_access_token
os.environ['{ID}_REFRESH_TOKEN'] = new_refresh_token
