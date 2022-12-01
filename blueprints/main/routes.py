from flask import Blueprint, request, session, flash, render_template, redirect, url_for
from sqlalchemy import desc
import random

import inspect

from app import app, db
from utils import login_required
from blueprints.main.utils import searcher, image_uploader, tag_redirect
from admintools.loggers import routing_logger, function_logger, logger_setup

from objects.db_objects.posts import Posts
from objects.db_objects.games import Games
from objects.db_objects.users import Users
from objects.db_objects.users_games import UsersGames
from objects.db_objects.recommended_games import RecommendedGames
from objects.db_objects.reports import Reports

from blueprints.main.getters.popular_game_getter import popular_games_getter
from blueprints.main.getters.popular_posts_getter import popular_posts_getter

from blueprints.games.routes import game
from blueprints.posts.routes import view_post
from blueprints.users.routes import profile

main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)

logger = logger_setup(__name__, "log.log")

# if any link ever breaks on routing, pass alongside urlencode in jinja ex: {{ linkref | urlencode }}


@app.route("/home")
@app.route("/")
def home():
    routing_logger(logger, session, request.environ)

    posts = Posts.query.all()
    popular_posts = popular_posts_getter(posts)
    listed_games = UsersGames.query.all()
    popular_games = popular_games_getter(listed_games)
    recent_games = Games.query.order_by(desc("date_added")).limit(6).options()

    if "user" in session:
        username = session["user"]
        user = Users.query.filter_by(name=username).first()
        recommended_games_user = None
        try:
            recommended_games_user = RecommendedGames.query.filter_by(user_id=user._id).first()
        except AttributeError as e:
            pass
        # TODO in time between factorizer running and account adding games to list, create a content model to use
        #  add game summary/description to the vectorization

        """checking that user has recommended games 
        (indicates if factorization has been run since user added games to list)"""
        if recommended_games_user is not None:
            recommended_games = recommended_games_user.game_recommendations
            if recommended_games:
                games = list(recommended_games.split(" "))
                recommended = []
                for game_id in games:
                    try:
                        game = Games.query.filter_by(_id=int(game_id)).first()
                    except ValueError as e:
                        game = None
                    recommended.append(game)
                    # print(type(game)) # worth noting that orm objects are stored as objects

                # if less than 3 recs generated, populates with 1 or 2 and passes those without erroring out
                try:
                    recommended = random.sample(recommended, 6)
                except ValueError:
                    pass

                return render_template(
                    "home.html",
                    recentgames=recent_games,
                    recommended=recommended,
                    popular_posts=popular_posts,
                    popular_games=popular_games,
                )
    return render_template(
        "home.html",
        recentgames=recent_games,
        popular_posts=popular_posts,
        popular_games=popular_games,
    )


@app.route("/search", methods=["POST", "GET"])
def w_search():
    routing_logger(logger, session, request.environ)
    return searcher(session, game=game, viewposts=view_post, profile=profile, Users=Users, Games=Games, Posts=Posts)



@app.route("/account/upload", methods=["POST"])
@login_required
def upload_image():
    routing_logger(logger, session, request.environ)

    return image_uploader(session=session, Users=Users)


@app.route("/display/<filename>")
def display_image(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@app.route("/report", methods=["POST", "GET"])
def report():
    routing_logger(logger, session, request.environ)
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    sender = (session['user_id'] if 'user_id' in session else 'None')
    report_message = request.form['reportMessage']
    issue_type = request.form['issueType']

    adder = Reports(log_reference='logplaceholder', origin_page=request.referrer, report_message=report_message,
                    issue_type=issue_type, sender=sender)
    db.session.add(adder)
    db.session.commit()

    flash("Report has been submitted. Thank you!", 'success')

    return redirect(request.referrer)


@app.route("/tagclicked/redirect/<path:tag>")
def tagclicked(tag):
    routing_logger(logger, session, request.environ)

    return tag_redirect(tag, game=game, viewposts=view_post, profile=profile)
