from app import db


class RequestedGames(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    requested_game = db.Column(db.String(), nullable=False)