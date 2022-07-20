from flask import Blueprint, current_app, request, redirect
import requests
import jwt
from datetime import datetime, timedelta
from sqlalchemy import func
from config import db
from models import User

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return redirect(
        "https://github.com/login/oauth/authorize?client_id="
        + current_app.config["GITHUB_CLIENT_ID"],
        code=302,
    )


@auth.get("/callback")
def login_callback():
    code = request.args.get("code")

    if code is not None:
        res = requests.post(
            "https://github.com/login/oauth/access_token",
            {
                "client_id": current_app.config["GITHUB_CLIENT_ID"],
                "client_secret": current_app.config["GITHUB_CLIENT_SECRET"],
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

        user = User.query.filter_by(github_id=user_data["id"]).first()

        if user is None:
            new_user = User(
                github_id=user_data["id"],
                github_username=user_data["login"],
                github_userurl=user_data["html_url"],
                created_at=func.now(),
            )

            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user)
            user = new_user

        # user_data['id'] # login id
        # user_data['login'] # login name
        # user_data['html_url'] # user repo url

        expiry = (datetime.now() + timedelta(hours=8)).timestamp()

        encoded = jwt.encode(
            {"id": user.id, "exp": expiry},
            current_app.config["JWT_KEY"],
            algorithm="HS256",
        )

        return (
            {
                "message": "Login success!, welcome " + user.github_username,
                "token": encoded,
            },
            {"Authorization": "Bearer " + encoded},
        )

    else:
        return ("Login failed", 500)
