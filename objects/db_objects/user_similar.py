from app import db


class UserSimilar(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True)
    games_similar_id = db.Column(db.Integer, db.ForeignKey("games_similar.id"), nullable=False, primary_key=True)

    def __repr__(self):
        return f"UserSimilar('{self.user_id}', '{self.games_similar_id}')"
