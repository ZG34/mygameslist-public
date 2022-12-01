from app import db


class CommentGames(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    # may not need this. ideally, just use hyperlinking