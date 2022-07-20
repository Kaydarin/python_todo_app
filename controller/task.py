from flask import Blueprint, request, g, jsonify
from sqlalchemy import func
from config import db
from models import Task, Todo

task = Blueprint("task", __name__)


@task.get("/list-tasks")
def list_tasks():
    modifier = request.args
    page = modifier.get("page", 1)
    limit = modifier.get("limit", 10)

    subquery = (
        db.session.query(Todo.id, Todo.task_id, Todo.title, Todo.is_done)
        .filter(Todo.deleted_at == None)
        .subquery("t")
    )

    tasks = (
        db.session.query(
            Task.id,
            Task.title,
            subquery.c.id.label("todo_id"),
            subquery.c.title.label("todo_title"),
            subquery.c.is_done,
        )
        .join(subquery, subquery.c.task_id == Task.id, isouter=True)
        .filter(Task.user_id == g.user_id, Task.deleted_at == None)
        .paginate(int(page), int(limit), False)
    )

    arr = []
    for i in tasks.items:
        data = i._asdict()

        task = next((val for val in arr if val["id"] == data["id"]), None)

        if task is None:
            task_remapped = {
                "id": data["id"],
                "title": data["title"],
            }

            if data["todo_id"] is not None:
                task_remapped = {
                    **task_remapped,
                    "todos": [
                        {
                            "id": data["todo_id"],
                            "title": data["todo_title"],
                            "is_done": data["is_done"],
                        }
                    ],
                }
            else:
                task_remapped = {
                    **task_remapped,
                    "todos": [],
                }

            arr.append(task_remapped)
        else:
            todo = next(
                (val for val in task["todos"] if val["id"] == data["todo_id"]),
                None,
            )
            if todo is None:
                task["todos"].append(
                    {
                        "id": data["todo_id"],
                        "title": data["todo_title"],
                        "is_done": data["is_done"],
                    }
                )

    return (jsonify(arr), 200)


@task.get("/task/<task_id>")
def get_task(task_id):

    subquery = (
        db.session.query(Todo.id, Todo.task_id, Todo.title, Todo.is_done)
        .filter(Todo.deleted_at == None)
        .subquery("t")
    )

    task = (
        db.session.query(
            Task.id,
            Task.title,
            subquery.c.id.label("todo_id"),
            subquery.c.title.label("todo_title"),
            subquery.c.is_done,
        )
        .join(subquery, subquery.c.task_id == Task.id, isouter=True)
        .filter(Task.id == task_id, Task.user_id == g.user_id, Task.deleted_at == None)
        .all()
    )

    mapped = {}

    if len(task) > 0:
        mapped = {"id": task[0]["id"], "title": task[0]["title"], "todos": []}

        for i in task:
            data = i._asdict()
            todo = next(
                (val for val in mapped["todos"] if val["id"] == data["todo_id"]),
                None,
            )

            if data["todo_id"] is not None and todo is None:
                mapped["todos"].append(
                    {
                        "id": data["todo_id"],
                        "title": data["todo_title"],
                        "is_done": data["is_done"],
                    }
                )

    return (jsonify(mapped), 200)


@task.post("/add-task")
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


@task.patch("/update-task")
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


@task.delete("/remove-task")
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
