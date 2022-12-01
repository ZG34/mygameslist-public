from app import db
from datetime import datetime


class Reports(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.now)

    log_reference = db.Column(db.Text)
    origin_page = db.Column(db.String(80))
    report_message = db.Column(db.String(80))
    issue_type = db.Column(db.String(80))
    sender = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"Report('{self._id}')"