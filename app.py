from flask import Flask, redirect, url_for
from config import db
from controller.auth import auth
from controller.task import task
from controller.todo import todo
from middleware import middleware

app = Flask(__name__)
app.register_blueprint(middleware)
app.register_blueprint(auth)
app.register_blueprint(task)
app.register_blueprint(todo)
app.config.from_object("config.Config")


@app.route("/")
def hello_world():
    return redirect(url_for("auth.login"))


db.init_app(app)
