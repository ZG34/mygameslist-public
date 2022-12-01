from app import db


class RecommendedGames(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    game_recommendations = db.Column(db.String())

    #  should  i add this to the user table?
    #  each user only has one column of game recs. should be fine to be combined.
