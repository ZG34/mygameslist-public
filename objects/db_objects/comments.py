from app import db
from datetime import datetime


class Comments(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    likes = db.relationship("CommentLikes", foreign_keys='CommentLikes.comment_id', lazy='dynamic')
    like_count = db.Column(db.Integer)


    def __repr__(self):
        return f"Comments('{self._id}')"
