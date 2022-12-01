from app import db
from flask_admin.contrib.sqla import ModelView


class GamesCategories(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __repr__(self):
        return f"GamesCategories('{self.game_id}', '{self.category_id}')"
