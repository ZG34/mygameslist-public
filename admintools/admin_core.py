from flask import request, url_for, redirect, session
from flask_admin import Admin
from flask_admin.contrib import sqla

from app import db, app
from objects.db_objects.users import Users
from objects.db_objects.users_games import UsersGames

from objects.db_objects.games import Games
from objects.db_objects.category import Category
from objects.db_objects.games_categories import GamesCategories

from objects.db_objects.posts import Posts
from objects.db_objects.comments import Comments
from objects.db_objects.post_likes import PostLikes
from objects.db_objects.comment_likes import CommentLikes
from objects.db_objects.post_games import PostGames

from objects.db_objects.recommended_games import RecommendedGames
from objects.db_objects.requested_games import RequestedGames
from objects.db_objects.games_similar import GamesSimilar
from objects.db_objects.user_similar import UserSimilar
from objects.db_objects.reports import Reports


class AdminView(sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        return session.get('user') == 'Admin'

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))


admin = Admin(app, name='Dashboard', index_view=AdminView(session=db.session, model=Users, url='/admin', endpoint='admin'))