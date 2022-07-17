from flask import Flask, request, redirect
import requests

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

        return "Login success"

    else:
        return ("Login failed", 400)
