from datetime import datetime
from app import db


class Games(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "title",
        ),
    )

    _id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    developer = db.Column(db.String(80))
    publisher = db.Column(db.String(80))
    release_date = db.Column(db.String())
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    game_image = db.Column(db.String())
    average_score = db.Column(db.Integer)
    ratings_count = db.Column(db.Integer)
    categories = db.relationship(
        "Category",
        secondary="games_categories",
        backref=db.backref("assigned", lazy="dynamic"),
    )
    similar = db.relationship("GamesSimilar", foreign_keys='GamesSimilar.reference_game_id') #removed lazy='dynamic'
    # user_listed = db.relationship("UsersGames", foreign_keys='UsersGames.game_id')
    game_on_post = db.relationship("PostGames", foreign_keys='PostGames.game_id', lazy='dynamic', backref='linkedgame')


    def __repr__(self):
        return f"Games('{self.title}')"


# FIXME is there a better solution for release_date storage besides string?
#  some have date as 'unreleased' which has no clear representation as datetime?
#  possible issue would be sorting by release date. would need to parse the string out first
