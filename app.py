from flask import Flask, request, redirect, url_for, g
import requests
import jwt
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

JWT_KEY = ""
GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""
MYSQL_CONN = ""

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = MYSQL_CONN
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(128), unique=True, nullable=False)
    github_username = db.Column(db.String(255), nullable=False)
    github_userurl = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<User %r>" % self.github_username


@app.before_request
def before_request():
    if (
        request.endpoint != "hello_world"
        and request.endpoint != "login"
        and request.endpoint != "login_callback"
    ):
        auth_token = request.headers["Authorization"]
        token = auth_token.split("Bearer ")[1]

        try:
            decoded = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
            g.user_id = decoded["id"]
        except jwt.ExpiredSignatureError:
            return ("Expired", 401)
        except jwt.InvalidSignatureError:
            return ("Invalid", 401)


@app.route("/")
def hello_world():
    return redirect(url_for("login"))


@app.route("/login")
def login():
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

        encoded = jwt.encode({"id": user.id, "exp": expiry}, JWT_KEY, algorithm="HS256")

        return (
            {"message": "Login success", "token": encoded},
            {"Authorization": "Bearer " + encoded},
        )

    else:
        return ("Login failed", 500)
