from app import db


class CommentLikes(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=False, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, primary_key=True)
    like = db.Column(db.Boolean, nullable=False)