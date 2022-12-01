from app import db


class PostLikes(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, primary_key=True)
    like = db.Column(db.Boolean, nullable=False)