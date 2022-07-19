from flask import Flask, request, redirect, url_for, g, jsonify
import requests
import jwt
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dataclasses import dataclass

JWT_KEY = ""
GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""
MYSQL_CONN = ""

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = MYSQL_CONN
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db = SQLAlchemy(app)


@dataclass
class User(db.Model):

    __tablename__ = "users"

    id: int
    github_id: str
    github_username: str
    github_userurl: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(128), unique=True, nullable=False)
    github_username = db.Column(db.String(255), nullable=False)
    github_userurl = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return (
            "<User (id='%s', github_id='%s', github_username='%s', github_userurl='%s', created_at='%s', updated_at='%s', deleted_at='%s')>"
            % (
                self.id,
                self.github_id,
                self.github_username,
                self.github_userurl,
                self.created_at,
                self.updated_at,
                self.deleted_at,
            )
        )


@dataclass
class Task(db.Model):

    __tablename__ = "tasks"

    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return (
            "<Task (id='%s', user_id='%s', title='%s', created_at='%s', updated_at='%s', deleted_at='%s')>"
            % (
                self.id,
                self.user_id,
                self.title,
                self.created_at,
                self.updated_at,
                self.deleted_at,
            )
        )


@dataclass
class Todo(db.Model):

    __tablename__ = "todos"

    id: int
    task_id: int
    title: str
    is_done: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    title = db.Column(db.String(255))
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return (
            "<Todo (id='%s', task_id='%s', title='%s', is_done='%s', created_at='%s', updated_at='%s', deleted_at='%s')>"
            % (
                self.id,
                self.task_id,
                self.title,
                self.is_done,
                self.created_at,
                self.updated_at,
                self.deleted_at,
            )
        )


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


@app.get("/list-tasks")
def list_tasks():
    modifier = request.args
    page = modifier.get("page", 1)
    limit = modifier.get("limit", 10)

    tasks = db.session.query(Task.id, Task.title).paginate(int(page), int(limit), False)

    arr = []
    for i in tasks.items:
        arr.append(i._asdict())

    return (jsonify(arr), 200)


@app.get("/task/<task_id>")
def task(task_id):

    task = (
        Task.query.with_entities(Task.id, Task.title)
        .filter(Task.id == task_id, Task.deleted_at == None)
        .one_or_none()
    )

    if task is None:
        task = {}
    else:
        task = task._asdict()

    return (jsonify(task), 200)


@app.post("/add-task")
def add_task():

    data = request.form
    title = data.get("title", None)

    if title is None:
        return ("Missing attribute", 422)

    new_task = Task(
        user_id=g.user_id,
        title=title,
        created_at=func.now(),
    )

    db.session.add(new_task)
    db.session.commit()
    db.session.refresh(new_task)

    return ({"message": "Successfully add new task!", "id": new_task.id}, 200)


@app.patch("/update-task")
def update_task():
    data = request.form

    task_id = data.get("id", None)
    title = data.get("title", None)

    if task_id is None or title is None:
        return ("Missing attribute", 422)

    data_to_update = {"title": title, "updated_at": func.now()}

    updated = (
        db.session.query(Task)
        .filter(Task.id == task_id, Task.user_id == g.user_id, Task.deleted_at == None)
        .update(data_to_update)
    )
    db.session.commit()

    if updated == 1:
        return ({"message": "Successfully updated task!"}, 200)
    else:
        return ({"message": "Nothing updated"}, 202)


@app.delete("/remove-task")
def delete_task():

    data = request.form

    task_id = data.get("id", None)

    if task_id is None:
        return ("Missing attribute", 422)

    deleted = (
        db.session.query(Task)
        .filter(Task.id == task_id, Task.user_id == g.user_id, Task.deleted_at == None)
        .update({"deleted_at": func.now()})
    )
    db.session.commit()

    if deleted == 1:
        return ({"message": "Successfully delete task!"}, 200)
    else:
        return ({"message": "Nothing deleted"}, 202)


@app.get("/list-todo")
def list_todo():
    modifier = request.args
    page = modifier.get("page", 1)
    limit = modifier.get("limit", 10)

    tasks = (
        db.session.query(Todo.id, Todo.title, Todo.is_done)
        .join(Task, Task.id == Todo.task_id)
        .filter(
            Task.user_id == g.user_id,
            Task.deleted_at == None,
            Todo.deleted_at == None,
        )
        .paginate(int(page), int(limit), False)
    )

    arr = []
    for i in tasks.items:
        arr.append(i._asdict())

    return (jsonify(arr), 200)


@app.get("/todo/<todo_id>")
def todo(todo_id):
    todo = (
        Todo.query.with_entities(Todo.id, Todo.task_id, Todo.title, Todo.is_done)
        .join(Task, Task.id == Todo.task_id)
        .filter(
            Todo.id == todo_id,
            Task.user_id == g.user_id,
            Task.deleted_at == None,
            Todo.deleted_at == None,
        )
        .one_or_none()
    )

    if todo is None:
        todo = {}
    else:
        todo = todo._asdict()

    return (jsonify(todo), 200)


@app.post("/add-todo")
def add_todo():
    data = request.form
    task_id = data.get("task_id", None)
    title = data.get("title", None)

    if task_id is None or title is None:
        return ("Missing attribute", 422)

    task = (
        Task.query.with_entities(Task.id)
        .filter(Task.id == task_id, Task.user_id == g.user_id, Task.deleted_at == None)
        .one_or_none()
    )

    if task is None:
        return ({"message": "Task is not exist"}, 400)

    new_todo = Todo(
        task_id=task_id,
        title=title,
        created_at=func.now(),
    )

    db.session.add(new_todo)
    db.session.commit()
    db.session.refresh(new_todo)

    return ({"message": "Successfully add new todo!", "id": new_todo.id}, 200)


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
            {
                "message": "Login success!, welcome " + user.github_username,
                "token": encoded,
            },
            {"Authorization": "Bearer " + encoded},
        )

    else:
        return ("Login failed", 500)
