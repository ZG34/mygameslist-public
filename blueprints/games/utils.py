from flask import session, flash, request, redirect
from sqlalchemy import text
from flask_sqlalchemy import Pagination
import inspect

from admintools.loggers import function_logger, logger_setup

from objects.db_objects.games import Games
from objects.db_objects.users import Users
from objects.db_objects.users_games import UsersGames
from objects.db_objects.category import Category
from objects.db_objects.games_similar import GamesSimilar
from objects.db_objects.user_similar import UserSimilar


from app import db, ENGINE, app

logger = logger_setup(__name__, "log.log")


def endorse_recommendation(game, user):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    similar_game_id = request.form.get('star')

    similar_game = GamesSimilar.query.filter_by(reference_game_id=game._id,
                                                similar_game_id=similar_game_id).first()

    similar_game.times_recommended += 1

    adder = UserSimilar(user_id=user._id, games_similar_id=similar_game._id)
    db.session.add(adder)
    db.session.commit()

    return redirect(request.url)


def submit_game_recommendation(game, user):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    games_titles = request.form.getlist('tags')
    for title in games_titles:
        similargame = Games.query.filter_by(title=title).first()

        if similargame is None:
            flash("Failed to submit: game does not exist in the database.", 'error')
            return redirect(request.url)

        if similargame._id == game._id:
            flash(f"can not suggest {similargame.title} for {game.title}. they are the same game!", "warning")
            return redirect(request.url)

        rec_checker = GamesSimilar.query. \
            filter_by(reference_game_id=game._id, similar_game_id=similargame._id).first()

        if not rec_checker:
            adder = GamesSimilar(reference_game_id=game._id,
                                 similar_game_id=similargame._id,
                                 times_recommended=1)
            db.session.add(adder)
            db.session.commit()
            adder2 = UserSimilar(user_id=user._id, games_similar_id=adder._id)
            db.session.add(adder2)
            db.session.commit()

        else:
            flash(f"{similargame.title} has already been recommended", "warning")
            return redirect(request.url)

    return redirect(request.url)


""" to add filters: each condition must be followed by re-assigning 'games' to 'user_games', and then games must be 
re-assigned as an empty list, to then be appended-to within the new condition"""
def mylist_filtering(my_list_form, user, page):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    start = (page - 1) * 10
    end = start + 10

    # TODO after implementing this, stress test speeds with larger user-size and game library
    # function is just returning a replaced 'games' list value based on given variables in filtering

    selector = my_list_form.game_sorter.selector.data
    order_by = my_list_form.game_sorter.order_by.data

    starts_char = my_list_form.game_filter.starts_with.data
    category_getter = my_list_form.game_filter.category_filter.data
    status_getter = my_list_form.game_filter.status.data

    category = Category.query.filter_by(tag=category_getter).first()

    # this is setting the order of items for all further queries
    games = user.games \
        .filter_by() \
        .filter(Games.title.ilike(f"{starts_char}%")) \
        .order_by(text(f"{selector} {order_by}")) \
        .paginate(page, 10, False)

    if category and starts_char and status_getter:
        user_games = games.items
        games = []
        user_statuses = UsersGames.query.filter_by(user_id=user._id, status=status_getter).all()
        cat_games_id = [x._id for x in category.assigned.all()]
        status_games = []
        for reference in user_statuses:
            game_id = reference.game_id
            status_games.append(game_id)
        for title in user_games:
            if (title._id in status_games) \
                    and ((title.title).upper()).startswith(f"{starts_char}") \
                    and (title._id in cat_games_id):
                game = Games.query.filter_by(_id=title._id).first()
                games.append(game)
        # refer to the two lines below, for how to paginate a python list
        items = games[start:end]
        games = Pagination(None, page, 10, len(items), items)
    elif starts_char and status_getter:
        user_games = games.items
        games = []
        user_statuses = UsersGames.query.filter_by(user_id=user._id, status=status_getter).all()
        status_games = []
        for reference in user_statuses:
            game_id = reference.game_id
            status_games.append(game_id)
        for title in user_games:
            if (title._id in status_games) and ((title.title).upper()).startswith(
                    f"{starts_char}"):
                game = Games.query.filter_by(_id=title._id).first()
                games.append(game)
        items = games[start:end]
        games = Pagination(None, page, 10, len(items), items)
    elif category and status_getter:
        user_games = games.items
        games = []
        cat_games_id = [x._id for x in category.assigned.all()]
        user_statuses = UsersGames.query.filter_by(user_id=user._id, status=status_getter).all()
        status_games = []
        for reference in user_statuses:
            game_id = reference.game_id
            status_games.append(game_id)
        for title in user_games:
            if (title._id in status_games) and (title._id in cat_games_id):
                game = Games.query.filter_by(_id=title._id).first()
                games.append(game)
        items = games[start:end]
        games = Pagination(None, page, 10, len(items), items)
    elif category and starts_char:
        user_games = []
        for game in games.items:
            user_games.append(game.title)
        gamesquery = category.assigned \
            .filter(Games.title.ilike(f"{starts_char}%")) \
            .order_by(text(f"{selector} {order_by}")) \
            .paginate(page, 10, False)
        games = []
        for game in gamesquery.items:
            if game.title in user_games:
                games.append(game)
        items = games[start:end]
        games = Pagination(None, page, 10, len(items), items)
    elif category:
        user_games = []
        for game in games.items:
            user_games.append(game.title)
        gamesquery = category.assigned \
            .order_by(text(f"{selector} {order_by}")) \
            .paginate(page, 10, False)
        games = []
        for game in gamesquery.items:
            if game.title in user_games:
                games.append(game)
        items = games[start:end]
        games = Pagination(None, page, 10, len(items), items)
    elif status_getter:
        user_games = games.items
        games = []
        user_statuses = UsersGames.query.filter_by(user_id=user._id, status=status_getter).all()
        status_games = []
        for reference in user_statuses:
            game_id = reference.game_id
            status_games.append(game_id)
        for title in user_games:
            if title._id in status_games:
                game = Games.query.filter_by(_id=title._id).first()
                games.append(game)
        items = games[start:end]
        games = Pagination(None, page, 10, len(items), items)

    return games


def browsegames_filter_and_sort(browse_form, page):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    # SORTERS
    selector = browse_form.game_sorter.selector.data
    order_by = browse_form.game_sorter.order_by.data

    # FILTERS
    starts_char = browse_form.game_filter.starts_with.data
    category_getter = browse_form.game_filter.category_filter.data
    print(category_getter)

    category = Category.query.filter_by(tag=category_getter).first()

    games = Games.query\
        .filter_by()\
        .order_by(text(f"{selector} {order_by}"))\
        .filter(Games.title.ilike(f"{starts_char}%"))\
        .paginate(page, 10, False)

    if category:
        games = category.assigned \
            .order_by(text(f"{selector} {order_by}")) \
            .filter(Games.title.ilike(f"{starts_char}%")) \
            .paginate(page, 10, False)

    return games


def game_form_submitter(form):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    # function ties together game_adder function and add_game_form
    if (form.is_submitted()) and ('user' in session):
        game_title = form.game.data
        game = Games.query.filter_by(title=game_title).first()

        user = Users.query.filter_by(_id=session['user_id']).first()
        status = form.status.data
        score = form.score.data

        logger.info(
            f"DB: user_id:[{session['user_id']}] pushing game: [{game._id}] into list"
        )

        game_adder(user=user, game=game, status=status, score=score)

        return redirect(request.url)


def game_adder(user, game, score, status):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    input_validator = UsersGames.query.filter_by(
        game_id=game._id, user_id=user._id
    ).first()

    if input_validator is None:
        # to ensure game-score averages are accurate, must not pass a Null value score to the database
        if score == "":
            adder = UsersGames(game_id=game._id, user_id=user._id, status=status)
            db.session.add(adder)
            db.session.commit()
            logger.info(
                f"DB: user_id:[{session['user_id']}] added game to list - UsersGames_id:[{adder._id}]"
            )
        else:
            adder = UsersGames(
                game_id=game._id, user_id=user._id, score=score, status=status
            )
            db.session.add(adder)
            db.session.commit()
            logger.info(
                f"DB: user_id:[{session['user_id']}] added game to list - UsersGames_id:[{adder._id}]"
            )

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

        flash(f"SUCCESS. {game.title} has been added to your list", "info")
        return redirect(request.url)
    else:
        logger.warning(
            f"user_id:[{session['user_id']}] ADD FAILED - game_id:[{game._id}] already on users "
            f"list"
        )
        flash(
            f"ERROR. {game.title} is already on your list. To edit or remove, view on 'My List' ",
            "info",
        )


# tool used to identify if game is on logged-in users' game list
def list_checker(userid):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    user_game_list = []
    user_has_game = UsersGames.query.filter_by(user_id=userid).all()
    for game in user_has_game:
        user_game_list.append(game.game_id)

    return user_game_list


@app.context_processor
def game_indexer():
    # FIXME is there a way to only call this on required sheets

    game_index = []
    games = Games.query.all()
    for game in games:
        game_index.append(game.title)

    return dict(game_index=game_index)


# TODO implement. would replace updategame route.
#  issue is in getting values from db into form element thru flaskwtf forms.
#  can try loading via form page? or pass required context while calling form in request (routing)
def game_form_updater(form):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    if form.is_submitted and ('user' in session):
        game_title = form.game.data
        game = Games.query.filter_by(title=game_title).first()

        user = Users.query.filter_by(_id=session['user_id']).first()
        status = form.status.data
        score = form.score.data

        logger.info(
            f"DB: user_id:[{session['user_id']}] pushing game: [{game._id}] into list"
        )

        game_updater(user=user, game=game, status=status, score=score)

        return redirect(request.url)


# relates to game_form_updater function.
def game_updater(user, game, status, score):
    if request.method == "POST":
        user = Users.query.filter_by(name=user.name).first()
        game = Games.query.filter_by(title=game.title).first()

        found_record = UsersGames.query.filter_by(
            game_id=game._id, user_id=user._id
        ).first()

        if request.form["submit_button"] == "Update":
            new_status = status
            new_score = score
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
            flash(f"SUCCESS. {game.title} has been updated", "info")
            return redirect(request.url)

        elif request.form["submit_button"] == "Delete":
            # TODO update average when deleting

            db.session.delete(found_record)
            count = db.session.query(UsersGames)
            countquery = count.where(UsersGames.game_id == game._id).count()
            game.ratings_count = countquery
            db.session.commit()

            logger.info(
                f"DB: user_id:[{session['user_id']}] DELETED GAMELIST ITEM - UsersGames_id:"
                f"[{found_record._id}]"
            )
            flash(f"SUCCESS. {game.title} has been removed from your list", "info")
            return redirect(request.url)