from flask import Flask, request, redirect
import requests
import jwt
from datetime import datetime, timedelta

JWT_KEY = ""
GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""

app = Flask(__name__)


@app.route("/")
def hello_world():
    return redirect(
        "https://github.com/login/oauth/authorize?client_id=" + GITHUB_CLIENT_ID,
        code=302,
    )


@app.get("/callback")
def login_callback():
    code = request.args.get("code")

    if code is not None:
        res = requests.post(
            "https://github.com/login/oauth/access_token",
            {
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

        if res.ok is not True:
            return ("Login failed", 500)

        data = res.json()

        res = requests.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": "token " + data["access_token"],
            },
        )

        if res.ok is not True:
            return ("Login failed", 500)

        user_data = res.json()

        # user_data['id'] # login id
        # user_data['login'] # login name
        # user_data['html_url'] # user repo url

        expiry = (datetime.now() + timedelta(hours=8)).timestamp()

        encoded = jwt.encode(
            {"id": user_data["id"], "exp": expiry}, JWT_KEY, algorithm="HS256"
        )

        return encoded

    else:
        return ("Login failed", 400)
