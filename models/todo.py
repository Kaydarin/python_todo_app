from dataclasses import dataclass
from datetime import datetime
from config import db


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
