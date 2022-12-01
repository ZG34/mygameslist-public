import os
from time import time

import jwt
from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy.sql.expression import text, func
from sqlalchemy import Index
from app import db
from admintools.loggers import logger_setup

logger = logger_setup(__name__, "log.log")


class Users(db.Model):
    __table_args__ = (
        db.UniqueConstraint("name"),
        db.UniqueConstraint("email"),
    )

    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String, default="default.png")
    posts = db.relationship("Posts", backref="author", lazy=True)
    games = db.relationship("Games", secondary="users_games", backref="players", lazy='dynamic')
    comments = db.relationship("Comments", backref="commenter", lazy=True)
    similar = db.relationship("UserSimilar", foreign_keys='UserSimilar.user_id')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)

    def new_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"Users('{self.name}')"

    def get_reset_token(self, expires=500):
        return jwt.encode({'reset_password': self.username, 'exp': time() + expires},
                           key='gigatesting')

    @staticmethod
    def verify_reset_token(token):
        try:
            name = jwt.decode(token, key=os.getenv('gigatesting'), options={"verify_signature": False})['reset_password']
        except Exception as e:
            logger.critical(f'{e}')
            return
        return Users.query.filter_by(name=name).first()


def check_pw(username, password):
    found_user = Users.query.filter(func.lower(Users.name) == username.lower()).first()
    return check_password_hash(found_user.password_hash, password)


Index('user_username_index', func.lower(Users.name), unique=True)
