from flask import Blueprint, request, session, flash, render_template, redirect, url_for
from sqlalchemy import text, and_
from string import ascii_lowercase as letters
import inspect

from app import app, db, ENGINE, page_not_found
from utils import login_required
from admintools.loggers import routing_logger, function_logger, logger_setup

from blueprints.games.utils import game_form_submitter, list_checker, \
    mylist_filtering, submit_game_recommendation, endorse_recommendation, \
    browsegames_filter_and_sort

from objects.db_objects.games import Games
from objects.db_objects.category import Category
from objects.db_objects.users import Users
from objects.db_objects.users_games import UsersGames
from objects.db_objects.posts import Posts
from objects.db_objects.post_games import PostGames
from objects.db_objects.requested_games import RequestedGames
from objects.db_objects.games_similar import GamesSimilar

from objects.forms import AddGameForm, BrowseForms \
    ,MyListForm

alphabet = letters
num_list = [x for x in range(0, 11)]

games_bp = Blueprint(
    "games_bp", __name__, template_folder="templates", static_folder="static"
)

logger = logger_setup(__name__, "log.log")


@app.route("/game/<path:game_name>", methods=["GET", "POST"])
def game(game_name):
    routing_logger(logger, session, request.environ)
    add_game_form = AddGameForm()

    # IN HTML, use {{ url | urlencode }}
    #  the URLENCODE will fix passing special chars

    user_game_list = None
    details = None
    user_similar = None

    game = Games.query.filter_by(title=game_name).first()
    if game is None:
        return page_not_found(game)

    categories = [x.tag for x in game.categories]
    times_completed = len(UsersGames.query.filter_by(game_id=game._id, status='completed').all())

    gameposts = PostGames.query.filter_by(game_id=game._id).all()
    linked_posts = []
    for line in gameposts:
        post = Posts.query.filter_by(_id=line.post_id).first()
        linked_posts.append(post)

    user = None
    if 'user_id' in session:
        user = Users.query.filter_by(_id=session['user_id']).first()
        details = UsersGames.query.filter_by(user_id=session['user_id']).all()
        user_game_list = list_checker(session['user_id'])
        # FIXME in html. disaster happening in jinja conditionals (is working though)

    similar_games = db.session. \
        query(Games). \
        join(GamesSimilar, and_(Games._id == GamesSimilar.similar_game_id)). \
        filter_by(reference_game_id=game._id). \
        order_by(GamesSimilar.times_recommended.desc()).all()

    if request.method == 'POST':
        if 'submit_rec' in request.form:
            return submit_game_recommendation(game=game, user=user)

        if 'star' in request.form:
            return endorse_recommendation(game=game, user=user)

        if add_game_form.submit.data and add_game_form.validate():
            game_form_submitter(add_game_form)
            return redirect(request.url)

    return render_template(
        "game.html",
        game=game,
        categories=categories,
        times_completed=times_completed,
        add_game_form=add_game_form,
        linked_posts=linked_posts,
        user_game_list=user_game_list,
        details=details,
        game_name=game_name,
        similar_games=similar_games,
        user_similar=user_similar,
    )


@app.route("/browse/<path:search_query>", methods=["POST", "GET"])
@app.route("/browse", methods=["POST", "GET"])
def browse(search_query=None):
    routing_logger(logger, session, request.environ)
    user_game_list = None
    details = None
    page = request.args.get("page", 1, type=int)
    add_game_form = AddGameForm()
    browse_form = BrowseForms(request.args)      # pass request.args to allow for GET method

    categories = Category.query.all()
    games = Games.query.order_by(Games.ratings_count.desc()).paginate(page, 10, False)
    from_base = True

    # gets user list of games if exists, to ensure user is informed as to which games are already lisited
    if 'user_id' in session:
        details = UsersGames.query.filter_by(user_id=session['user_id']).all()
        user_game_list = list_checker(session['user_id'])

    if browse_form.game_sorter.selector.data or browse_form.game_sorter.order_by.data or \
        browse_form.game_filter.starts_with.data or browse_form.game_filter.category_filter.data:
        games = browsegames_filter_and_sort(browse_form, page=page)
        from_base = False

    if search_query=='1':
        try:
            url = request.environ['HTTP_REFERER']
            size = len(url)
            if url[-1] in str(num_list):
                url = url[:size - 7]
                if url[-1] == "&":
                    size = len(url)
                    url = url[:size - 1]
                # checks for trailing & at end of fixed url (in case of double nums bumping +1)
                # (would need another adjust for triple chars / 100s pages) # FIXME
            return redirect(f"{url}&page={page}")
        except Exception as e:
            print(e)

    if add_game_form.submit.data and add_game_form.validate():
        game_form_submitter(add_game_form)
        return redirect(request.url)

    return render_template(
        "browse.html",
        games=games.items,
        categories=categories,
        pages=games,
        alphabet=alphabet,
        nums=num_list,
        add_game_form=add_game_form,
        user_game_list=user_game_list,
        details=details,
        browse_form=browse_form,
        from_base=from_base
    )


@app.route("/updategame/<path:game_name>", methods=["POST", "GET"])
@login_required
def updategame(game_name, search_query=None):
    # TODO replace with forms.update_game
    routing_logger(logger, session, request.environ)
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)
    page = request.args.get("page", 1, type=int)

    username = session["user"]
    if request.method == "POST":
        user = Users.query.filter_by(name=username).first()
        game = Games.query.filter_by(title=game_name).first()
        found_record = UsersGames.query.filter_by(
            game_id=game._id, user_id=user._id
        ).first()

        if request.form["submit_button"] == "Update":
            new_status = request.form.get("status")
            new_score = request.form.get("score")
            found_record.status = new_status
            found_record.score = new_score
            db.session.commit()

            query = text(
                f"""SELECT ROUND(AVG(score),2) FROM users_games
                            WHERE "game_id" = {game._id}"""
            )

            result = ENGINE.execute(query).fetchone()
            if result[0] != None:
                game.average_score = result[0]

            count = db.session.query(UsersGames)
            countquery = count.where(UsersGames.game_id == game._id).count()
            game.ratings_count = countquery

            db.session.commit()

            logger.info(
                f"DB: user_id:[{session['user_id']}] UPDATED GAMELIST ITEM - UsersGames_id:"
                f"[{found_record._id}]"
            )
            flash(f"SUCCESS. {game_name} has been updated", "info")
            return redirect(request.url)

        elif request.form["submit_button"] == "Delete":
            db.session.delete(found_record)
            count = db.session.query(UsersGames)
            countquery = count.where(UsersGames.game_id == game._id).count()
            game.ratings_count = countquery
            db.session.commit()

            query = text(
                f"""SELECT ROUND(AVG(score),2) FROM users_games
                            WHERE "game_id" = {game._id}"""
            )

            result = ENGINE.execute(query).fetchone()
            if result[0] != None:
                game.average_score = result[0]
                db.session.commit()

            logger.info(
                f"DB: user_id:[{session['user_id']}] DELETED GAMELIST ITEM - UsersGames_id:"
                f"[{found_record._id}]"
            )
            flash(f"SUCCESS. {game_name} has been removed from your list", "info")
            return redirect(request.url)

    # re-grab items to render after update/delete is completed
    username = session["user"]
    user = Users.query.filter_by(name=username).first()
    games = user.games.order_by(Games.ratings_count.desc()).paginate(page, 10, False)
    details = UsersGames.query.filter_by(user_id=user._id).all()
    from_base = True


    my_list_form = MyListForm(request.args)      # pass request.args to allow for GET method
    if my_list_form.game_sorter.selector.data or my_list_form.game_sorter.order_by.data or \
            my_list_form.game_filter.starts_with.data or my_list_form.game_filter.category_filter.data or \
            my_list_form.game_filter.status.data:
        games = mylist_filtering(my_list_form=my_list_form, user=user, page=page)
        from_base = False

    if search_query=='1':
        url = request.environ['HTTP_REFERER']
        size = len(url)
        if url[-1] in str(num_list):
            url = url[:size - 7]
            if url[-1] == "&":
                size = len(url)
                url = url[:size - 1]
            # checks for trailing & at end of fixed url (in case of double nums bumping +1)
            # (would need another adjust for triple chars / 100s pages) # FIXME
        return redirect(f"{url}&page={page}")

    return render_template("mylist.html", user=user, users_games=games.items, details=details, pages=games,
                           my_list_form=my_list_form, from_base=from_base)


@app.route("/profile/gamelist/<path:username>/<path:search_query>", methods=["POST", "GET"])
@app.route("/profile/gamelist/<path:username>", methods=["POST", "GET"])
def mylist(username, search_query=None):
    routing_logger(logger, session, request.environ)
    my_list_form = MyListForm(request.args)      # pass request.args to allow for GET method
    page = request.args.get("page", 1, type=int)

    user = Users.query.filter_by(name=username).first()
    if user is None:
        return page_not_found(user)

    games = user.games.order_by(Games.ratings_count.desc()).paginate(page, 10, False)
    from_base = True

    details = UsersGames.query.filter_by(user_id=user._id).all()

    # update_game_form = UpdateGameForm()
    #
    # if update_game_form.submit.data and update_game_form.validate():
    #     game_form_updater(update_game_form)
    #     return redirect(request.url)

    # FIXME must be a better way to capture if these change, rather than checking each individually
    if my_list_form.game_sorter.selector.data or my_list_form.game_sorter.order_by.data or \
            my_list_form.game_filter.starts_with.data or my_list_form.game_filter.category_filter.data or \
            my_list_form.game_filter.status.data:
        games = mylist_filtering(my_list_form=my_list_form, user=user, page=page)
        from_base = False

    if search_query=='1':
        url = request.environ['HTTP_REFERER']
        size = len(url)
        if url[-1] in str(num_list):
            url = url[:size - 7]
            if url[-1] == "&":
                size = len(url)
                url = url[:size - 1]
            # checks for trailing & at end of fixed url (in case of double nums bumping +1)
            # (would need another adjust for triple chars / 100s pages) # FIXME
        return redirect(f"{url}&page={page}")

    return render_template(
        "mylist.html", user=user, users_games=games.items, user_id=user._id, details=details,
        pages=games, my_list_form=my_list_form, from_base=from_base

    )


@app.route("/requestgame", methods=["POST", "GET"])
def requestgame():
    routing_logger(logger, session, request.environ)
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    adder = RequestedGames(user_id=session['user_id'], requested_game=request.form['title'])
    db.session.add(adder)
    db.session.commit()
    logger.info(f"DB: user_id:[{session['user_id']}] requested [{request.form['title']}] be added to the DB")
    flash("Your request has been submitted!")

    return redirect(url_for('browse'))
