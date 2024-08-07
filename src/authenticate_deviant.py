from flask import Flask, request, redirect
import requests

from deviant_utils.deviant_refresh_token import write_token_to_file
from utils.account_loader import select_account
from utils.cli_args import parse_arguments

ACCOUNT = parse_arguments().account
account = select_account(ACCOUNT)
deviant_config = account.deviant_config


if deviant_config is None:
    err = f"Account {account.id} has no Deviant config"
    raise RuntimeError(err)

# Creates a spin off webserver to retrieve an access and refresh token for the first time, visit localhost:3000/login

app = Flask(__name__)

PORT = 3000
REDIRECT_URI = f"http://localhost:{PORT}/deviantart/callback"
SCOPE = "stash publish browse"


@app.route("/login")
def login():
    auth_url = f"https://www.deviantart.com/oauth2/authorize?response_type=code&client_id={deviant_config.client_id}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(auth_url)


@app.route("/deviantart/callback")
def callback():
    authorization_code = request.args.get("code")
    token_url = "https://www.deviantart.com/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": deviant_config.client_id,
        "client_secret": deviant_config.client_secret,
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, headers=headers, data=data)
    tokens = response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    write_token_to_file(ACCOUNT, refresh_token)
    return f"Access Token: {access_token}<br>Refresh Token: {refresh_token}"


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
