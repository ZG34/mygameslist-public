from app import db


class PostGames(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)