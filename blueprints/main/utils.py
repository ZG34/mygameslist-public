from flask import request, render_template, flash, redirect, url_for, session, abort
import time
import inspect
from werkzeug.utils import secure_filename
from uuid import uuid1
import os

from app import ALLOWED_EXTENSIONS, db, app
from admintools.loggers import function_logger, logger_setup

logger = logger_setup(__name__, "log.log")


def searcher(session, game, viewposts, profile, Users, Games, Posts):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    query = request.args.get("search")

    # get table (Games, Posts, Users...)
    chopped_query = query.partition("(")
    table = chopped_query[0]
    object_identifier = chopped_query[2].partition(")")[0].replace("'","")
    tables = ["Games", "Posts", "Users"]
    if table in tables:
        logger.info(
            f"user_id:[{session['user_id'] if 'user_id' in session else None}] search query: [{query}]"
        )
        if table == "Games":
            game_name = object_identifier
            return game(game_name=game_name)
        if table == "Posts":
            post_name = object_identifier
            return viewposts(post_name=post_name)
        if table == "Users":
            username = object_identifier
            return profile(username=username)
    else:
        start_time = time.time()

        users = Users.query.msearch(query, fields=["name"], limit=20).all()
        games = Games.query.msearch(
            query, fields=["title", "publisher", "developer"], limit=20
        ).all()
        posts = Posts.query.msearch(query, fields=["title", "body"], limit=20).all()

        # TODO make game category searchable

        end_time = round(time.time() - start_time, 3)

        # TODO improve search results. if i search "soccer" fifa should pop up.

        logger.info(
            f"user_id:[{session['user_id'] if 'user_id' in session else None}] search query: [{query}] - "
            f"completed in [{end_time}] seconds"
        )

        return render_template("searchresults.html", users=users, games=games, posts=posts)


def image_uploader(session, Users):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["file"]

    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)

    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    if file and allowed_file(file.filename):
        username = session["user"]
        user = Users.query.filter_by(name=username).first()

        filename = secure_filename(file.filename)
        save_name = str(uuid1()) + "_" + filename
        filename = save_name
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        user.image_file = filename
        db.session.commit()

        flash("Profile image updated!")
        return render_template("account.html", filename=filename, user=user)
    else:
        flash("Allowed image types are .png, .jpg, .jpeg")
        return redirect(url_for("account"))


def tag_redirect(tag, game, viewposts, profile):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    # get table (Games, Posts, Users...)
    chopped_query = tag.partition("(")
    table = chopped_query[0]
    object_identifier = chopped_query[2].partition(")")[0].replace("'", "")
    tables = ["Games", "Posts", "Users"]
    if table in tables:
        logger.info(
            f"user_id:[{session['user_id'] if 'user_id' in session else None}] search query: [{tag}]"
        )
        if table == "Games":
            game_name = object_identifier
            return redirect(url_for('game', game_name=game_name))
        if table == "Posts":
            post_name = object_identifier
            return redirect(url_for('view_post', post_name=post_name))
        if table == "Users":
            username = object_identifier
            return redirect(url_for('profile', username=username))
    else:
        logger.error(f'[{tag}] was rendered as a clickable link, via:[{request.referrer}]')
        abort(404, description="that should not be clickable")
