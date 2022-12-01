from app import db
from datetime import datetime


class Posts(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comments = db.relationship(
        "Comments", backref=db.backref("parent post", uselist=False), lazy="dynamic"
    )
    newest_comment = db.Column(db.DateTime)
    like_count = db.Column(db.Integer)
    likes = db.relationship("PostLikes", foreign_keys='PostLikes.post_id', lazy='dynamic')
    post_games = db.relationship("PostGames", foreign_keys='PostGames.post_id', lazy='dynamic')


    # FIXME in admin sheet the relationship on posts displays poorly for comments

    def __repr__(self):
        return f"Posts('{self.title}')"
