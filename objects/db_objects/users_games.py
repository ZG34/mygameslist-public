from app import db
from datetime import datetime
from flask_admin.contrib.sqla import ModelView


class UsersGames(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    score = db.Column(db.String(80))
    status = db.Column(db.String(80))
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"UsersGames('{self.game_id}', '{self.user_id})"
