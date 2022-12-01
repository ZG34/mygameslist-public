import logging
import time
from functools import wraps
from flask import session, flash, redirect, url_for, render_template, request

from app import app

from objects.db_objects.posts import Posts
from objects.db_objects.games import Games
from objects.db_objects.users import Users


def login_required(f):
    @wraps(f)
    def wrapped_route(**kwargs):
        if "user" not in session:
            flash(f"Must be logged in", "info")
            return redirect(url_for("login"))

        return f(**kwargs)

    return wrapped_route


# context processor allows to pass return value freely into HTML without being directly fed via a route
# currently this index runs entirely each time a page is loaded? probably not ideal?

@app.context_processor
def search_indexer():
    start_time = time.time()

    search_index = []

    games = Games.query.all()
    for game in games:
        search_index.append(game)

    users = Users.query.all()
    for user in users:
        search_index.append(user)

    posts = Posts.query.all()
    for post in posts:
        search_index.append(post)

    end_time = round(time.time() - start_time, 3)

    return dict(search_index=search_index)


def trailing_whitespace_cutter(string):
    while string[-1] == " ":
        string = string[:-1]

    return string


@app.context_processor
def inject_template_scope():
    injections = dict()

    def cookies_check():
        value = request.cookies.get('cookie_consent')
        return value == 'true'

    injections.update(cookies_check=cookies_check)

    return injections

@app.context_processor
def cookies_check():
    cookies_check = []
    return dict(cookies_check)