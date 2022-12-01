from app import db
from objects.db_objects.games import Games
from flask_admin.contrib.sqla import ModelView


class GamesSimilar(db.Model):
    # __table_args__ = (
    #     # this can be db.PrimaryKeyConstraint if you want it to be a primary key
    #     db.UniqueConstraint('reference_game_id', 'similar_game_id'),
    # )

    _id = db.Column("id", db.Integer, primary_key=True)
    reference_game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    similar_game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    times_recommended = db.Column(db.Integer)
    by_user = db.relationship("UserSimilar", foreign_keys='UserSimilar.games_similar_id', lazy='dynamic',
                              )

    def __repr__(self):
        return f"GamesSimilar('{self._id}', '{self.reference_game_id}', '{self.similar_game_id}')"

    # __mapper_args__ = {'polymorphic_identity': 'gamessimilar',
    #                    'inherit_condition': reference_game_id == Games._id}

