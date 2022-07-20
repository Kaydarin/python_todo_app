from dataclasses import dataclass
from datetime import datetime
from config import db


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
