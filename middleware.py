from flask import Blueprint, current_app, request, g
import jwt

middleware = Blueprint("middleware", __name__)


@middleware.before_app_request
def before_app_request():
    if (
        request.endpoint != "hello_world"
        and request.endpoint != "auth.login"
        and request.endpoint != "auth.login_callback"
    ):
        auth_token = request.headers["Authorization"]
        token = auth_token.split("Bearer ")[1]

        try:
            decoded = jwt.decode(
                token, current_app.config["JWT_KEY"], algorithms=["HS256"]
            )
            g.user_id = decoded["id"]
        except jwt.ExpiredSignatureError:
            return ("Expired", 401)
        except jwt.InvalidSignatureError:
            return ("Invalid", 401)
