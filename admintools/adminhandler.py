from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib import sqla
# from flask_admin.form import SecureForm
from sqlalchemy import inspect
import os.path
from flask import send_file, session, render_template, request, url_for, redirect, g
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

from wtforms import HiddenField, Form

from app import db, page_not_found, csrf, app
from admintools.admin_core import admin

from admintools.loggers import logger_setup, routing_logger, function_logger

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

from objects.game_recommender.factorizer import factorizer

logger = logger_setup(__name__, "log.log")


def current_user_is_admin():
    # print(request.cookies)
    if 'user' in session:
        if session['user'] == 'Admin':
            return True
    else:
        return False


class PkViews(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_display_all_relations = True


class ReportView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_list = [c_attr.key for c_attr in inspect(Reports).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(Reports).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(Reports).mapper.column_attrs]


class CategoryView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_list = [c_attr.key for c_attr in inspect(Category).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(Category).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(Category).mapper.column_attrs]


class UsersGamesView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_list = [c_attr.key for c_attr in inspect(UsersGames).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(UsersGames).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(UsersGames).mapper.column_attrs]


class GamesCategoriesView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_list = [c_attr.key for c_attr in inspect(GamesCategories).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(GamesCategories).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(GamesCategories).mapper.column_attrs]


class RecommendedGamesView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_list = [c_attr.key for c_attr in inspect(RecommendedGames).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(RecommendedGames).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(RecommendedGames).mapper.column_attrs]


class PostsView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(Posts).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(Posts).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(Posts).mapper.column_attrs]


class PostLikesView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(PostLikes).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(PostLikes).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(PostLikes).mapper.column_attrs]


class CommentsLikesView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(CommentLikes).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(CommentLikes).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(CommentLikes).mapper.column_attrs]


class PostGameView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(PostGames).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(PostGames).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(PostGames).mapper.column_attrs]


class RequestedGameView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(RequestedGames).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(RequestedGames).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(RequestedGames).mapper.column_attrs]


class GamesSimilarView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(GamesSimilar).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(GamesSimilar).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(GamesSimilar).mapper.column_attrs]


class UserSimilarView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = True
    column_list = [c_attr.key for c_attr in inspect(UserSimilar).mapper.column_attrs]
    column_filters = [c_attr.key for c_attr in inspect(UserSimilar).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(UserSimilar).mapper.column_attrs]


class UsersView(ModelView):
    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_hide_backrefs = False
    column_list = ('_id', 'name', 'password_hash', 'email', 'image_file', 'posts', 'comments', 'similar')
    # FIXME cant display usergames here
    column_filters = [c_attr.key for c_attr in inspect(Users).mapper.column_attrs]
    column_searchable_list = [c_attr.key for c_attr in inspect(Users).mapper.column_attrs]


class GamesView(ModelView):
    list_template = '/admin/games_list.html'

    def is_accessible(self):
        return current_user_is_admin()
    column_display_pk = True
    column_searchable_list = [c_attr.key for c_attr in inspect(Games).mapper.column_attrs]


class SaveSqlView(BaseView):
    def is_accessible(self):
        return current_user_is_admin()

    @expose('/')
    def index(self):
        if current_user_is_admin():
            file_exists = os.path.exists('users.sqlite3')
            if file_exists:
                file = os.path.abspath('users.sqlite3')
                logger.info("Exported database")
                return send_file(file, as_attachment=True)
            return self.render('admin/savesql.html', var1="var1test")
        else:
            return page_not_found(True)


class Factorizer(BaseView):
    def is_accessible(self):
        return current_user_is_admin()

    @expose('/')
    def __index__(self):
        if current_user_is_admin():
            factorizer()
            logger.info("Ran factorizer")

            return self.render('admin/factorizer.html')
        else:
            return page_not_found(True)


class LogView(BaseView):
    def is_accessible(self):
        return current_user_is_admin()

    @expose('/', methods=['GET', 'POST'])
    def __index__(self):
        if current_user_is_admin():
            with open("log.log") as logfile:
                lines = logfile.readlines()
                lines = [line.rstrip() for line in lines]
            if request.method == 'POST':
                searchstring = request.form.get('searcher')
                export = request.form.get('export')
                delete = request.form.get('delete')
                if searchstring:
                    lines = []
                    with open("log.log") as logfile:
                        items = logfile.readlines()
                        items = [line.rstrip() for line in items]
                    for line in items:
                        if searchstring in line:
                            print(line)
                            lines.append(line)
                if export:
                    logger.warning("Exported log")
                    file_exists = os.path.exists('log.log')
                    if file_exists:
                        file = os.path.abspath('log.log')
                        return send_file(file, as_attachment=True)
                if delete:
                    # LOG
                    file_exists = os.path.exists('log.log')
                    if file_exists:
                        file = os.path.abspath('log.log')
                        os.remove(file)
                        with open('log.log', 'w') as newlog:
                            newlog.write(f"New logfile generated at {datetime.now()}")

            return self.render('admin/logging.html', logger=reversed(lines))
        else:
            return page_not_found(True)


def admin_views():
    admin.add_view(UsersView(model=Users, session=db.session))

    admin.add_view(GamesView(model=Games, session=db.session))
    admin.add_view(UsersGamesView(model=UsersGames, session=db.session))
    admin.add_view(RecommendedGamesView(model=RecommendedGames, session=db.session))
    admin.add_view(RequestedGameView(model=RequestedGames, session=db.session))
    admin.add_view(GamesSimilarView(model=GamesSimilar, session=db.session))
    admin.add_view(UserSimilarView(model=UserSimilar, session=db.session))

    admin.add_view(PostsView(model=Posts, session=db.session))
    admin.add_view(PkViews(model=Comments, session=db.session))
    admin.add_view(PostLikesView(model=PostLikes, session=db.session))
    admin.add_view(CommentsLikesView(model=CommentLikes, session=db.session))
    admin.add_view(PostGameView(model=PostGames, session=db.session))

    admin.add_view(CategoryView(model=Category, session=db.session))
    admin.add_view(GamesCategoriesView(model=GamesCategories, session=db.session))

    admin.add_view(SaveSqlView(name="Save SQL", endpoint='savesql'))
    admin.add_view(Factorizer(name="Run Recommender", endpoint='factorizer'))
    admin.add_view(LogView(name="View Logs", endpoint="logging"))

    admin.add_view(ReportView(model=Reports, session=db.session))
