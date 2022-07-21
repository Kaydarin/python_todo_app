from dataclasses import dataclass
from datetime import datetime
from config import db


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

    @classmethod
    def with_todo(cls):
        from models import Todo

        subquery = (
            db.session.query(Todo.id, Todo.task_id, Todo.title, Todo.is_done)
            .filter(Todo.deleted_at == None)
            .subquery("t")
        )

        tasks = db.session.query(
            cls.id,
            cls.title,
            subquery.c.id.label("todo_id"),
            subquery.c.title.label("todo_title"),
            subquery.c.is_done,
        ).join(subquery, subquery.c.task_id == cls.id, isouter=True)

        return tasks
