import os
from flask_sqlalchemy import SQLAlchemy

if os.environ.get("IS_DOCKER"):
    db_username = os.environ.get("DB_USERNAME")
    db_userpassword = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    jwt_key = os.environ.get("JWT_KEY")
    github_id = os.environ.get("GITHUB_CLIENT_ID")
    github_secret = os.environ.get("GITHUB_CLIENT_SECRET")
else:
    db_username = ""
    db_userpassword = ""
    db_host = ""
    db_port = ""
    jwt_key = ""
    github_id = ""
    github_secret = ""


class Config(object):
    JWT_KEY = jwt_key
    GITHUB_CLIENT_ID = github_id
    GITHUB_CLIENT_SECRET = github_secret
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        + db_username
        + ":"
        + db_userpassword
        + "@"
        + db_host
        + ":"
        + db_port
        + "/python_todo"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


db = SQLAlchemy()
