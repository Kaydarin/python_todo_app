from flask import Blueprint, request, g, jsonify
from sqlalchemy import func
from config import db
from models import Task, Todo

todo = Blueprint("todo", __name__)


@todo.get("/list-todo")
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


@todo.get("/todo/<todo_id>")
def get_todo(todo_id):
    todo = Todo.with_task(
        [Todo.id, Todo.task_id, Todo.title, Todo.is_done], todo_id, g.user_id
    ).one_or_none()

    if todo is None:
        todo = {}
    else:
        todo = todo._asdict()

    return (jsonify(todo), 200)


@todo.post("/add-todo")
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


@todo.patch("/update-todo")
def update_todo():
    data = request.form

    todo_id = data.get("id", None)
    title = data.get("title", None)

    if todo_id is None or title is None:
        return ("Missing attribute", 422)

    todo = Todo.with_task([Todo.id, Todo.task_id], todo_id, g.user_id).one_or_none()

    if todo is None:
        return ({"message": "Todo is not exist"}, 400)

    data_to_update = {"title": title, "updated_at": func.now()}

    updated = (
        db.session.query(Todo)
        .filter(
            Todo.id == todo_id,
            Todo.deleted_at == None,
        )
        .update(data_to_update)
    )
    db.session.commit()

    if updated == 1:
        return ({"message": "Successfully updated todo!"}, 200)
    else:
        return ({"message": "Nothing updated"}, 202)


@todo.patch("/mark-todo")
def mark_todo():
    data = request.form

    todo_id = data.get("id", None)
    done = data.get("done", None)

    if todo_id is None or done is None:
        return ("Missing attribute", 422)

    if done.isdigit() is False:
        return ("Invalid value", 400)
    else:
        done = int(done)
        if done not in [0, 1]:
            return ("Invalid value", 400)

    todo = Todo.with_task(
        [Todo.id, Todo.task_id, Todo.is_done], todo_id, g.user_id
    ).one_or_none()

    if todo is None:
        return ({"message": "Todo is not exist"}, 400)

    if todo._asdict()["is_done"] == done:
        return ({"message": "Nothing updated"}, 202)

    data_to_update = {"is_done": done, "updated_at": func.now()}

    updated = (
        db.session.query(Todo)
        .filter(
            Todo.id == todo_id,
            Todo.deleted_at == None,
        )
        .update(data_to_update)
    )
    db.session.commit()

    if updated == 1:
        return ({"message": "Successfully mark todo!"}, 200)
    else:
        return ({"message": "Nothing updated"}, 202)


@todo.delete("/remove-todo")
def delete_todo():
    data = request.form

    todo_id = data.get("id", None)

    if todo_id is None:
        return ("Missing attribute", 422)

    todo = Todo.with_task([Todo.id, Todo.task_id], todo_id, g.user_id).one_or_none()

    if todo is None:
        return ({"message": "Todo is not exist"}, 400)

    deleted = (
        db.session.query(Todo)
        .filter(Todo.id == todo_id, Todo.deleted_at == None)
        .update({"deleted_at": func.now()})
    )
    db.session.commit()

    if deleted == 1:
        return ({"message": "Successfully delete todo!"}, 200)
    else:
        return ({"message": "Nothing deleted"}, 202)
