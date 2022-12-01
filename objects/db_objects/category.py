from app import db
from flask_admin.contrib.sqla import ModelView


class Category(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "tag",
        ),
    )

    _id = db.Column("id", db.Integer, primary_key=True)
    tag = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Category('{self.tag}')"
