from flask import request, flash, redirect, url_for
from datetime import datetime

import re
import inspect

from app import db
from utils import trailing_whitespace_cutter
from admintools.loggers import function_logger, logger_setup

from objects.db_objects.posts import Posts
from objects.db_objects.users import Users
from objects.db_objects.comments import Comments
from objects.db_objects.comment_likes import CommentLikes
from objects.db_objects.post_likes import PostLikes
from objects.db_objects.post_games import PostGames
from objects.db_objects.games import Games


logger = logger_setup(__name__, "log.log")


def new_post_poster(session, form, username):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    if form.validate_on_submit():
        user = Users.query.filter_by(name=username).first()
        title = form.title.data
        title = trailing_whitespace_cutter(title)

        regex = re.compile('[@#$"%^&*()<>/\|}{~:]')
        if regex.search(username) is None:
            if regex.search(title) is None:
                post = Posts(title=title, body=form.body.data, user_id=username)
                user.posts.append(post)
                db.session.add(post)
                db.session.commit()

                games_titles = request.form.getlist('tags')
                if not games_titles:
                    pass
                else:
                    for item in games_titles:
                        game = Games.query.filter_by(title=item).first()
                        if game is None:
                            flash("At least on game you attempted to link does not exist in the database. Linking of "
                                  "this game failed.", 'error')
                            continue
                        postgames = PostGames(post_id=post._id, game_id=game._id)
                        db.session.add(postgames)

                        logger.info(f"DB: user_id [{user._id}] tagging post_id [{post._id}] with game_id [{game._id}]  ")

                db.session.commit()
                logger.info(f"DB: user_id [{user._id}] COMMITTED TAGS ON post_id [{post._id}] successfully")

                logger.info(
                    f"DB: user_id [{user._id}] submitted new post - post_id: [{post._id}]"
                )
                return redirect(url_for("forums"))
            else:
                flash("ERROR: Do not use special characters in title", "error")
                logger.warning(f"user_id [{user._id}] post titled [{title}] failed forum post due to regex")
                return redirect(request.url)


def reply_poster(reply_form, user, post, session):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    comment = Comments(body=reply_form.body.data, user_id=user._id, post_id=post._id)
    db.session.add(comment)
    post.comments.append(comment)
    post.newest_comment = datetime.now()
    user.comments.append(comment)
    db.session.commit()
    reply_form.body.data = ""
    logger.info(
        f"DB: user_id [{user._id}] added comment_id [{comment._id}] on post_id [{post._id}]"
    )
    return redirect(request.url)


def post_like_updater(post_like_checker, user, post, post_like_form, session):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    if post_like_checker is None:
        # ifs are checking for True returns (indicating button was clicked)
        if post_like_form.like.data:
            post_liked = PostLikes(user_id=user._id, post_id=post._id, like=True)
            db.session.add(post_liked)
            db.session.commit()
            post.like_count = (len(post.likes.filter_by(post_id=post._id, like=True).all()) -
                        (len(post.likes.filter_by(post_id=post._id, like=False).all())))
            db.session.commit()
            logger.info(
                f"DB: user_id [{user._id}] liked post_id [{post._id}]"
            )

        elif post_like_form.dislike.data:
            post_disliked = PostLikes(user_id=user._id, post_id=post._id, like=False)
            db.session.add(post_disliked)
            db.session.commit()
            post.like_count = (len(post.likes.filter_by(post_id=post._id, like=True).all()) -
                        (len(post.likes.filter_by(post_id=post._id, like=False).all())))
            db.session.commit()
            logger.info(
                f"DB: user_id [{user._id}] disliked post_id [{post._id}]"
            )
        return redirect(request.url)
    else:
        post_like_checker.like = post_like_form.like.data
        db.session.commit()
        post.like_count = (len(post.likes.filter_by(post_id=post._id, like=True).all()) -
                           (len(post.likes.filter_by(post_id=post._id, like=False).all())))
        db.session.commit()
        logger.info(
            f"DB: user_id [{user._id}] updated like/dislike on post_id [{post._id}]"
        )
        return redirect(request.url)


def comment_like_updater(comment_like_checker, user, comment, comment_like_form, session, post):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    if comment_like_checker is None:
        # ifs are checking for True returns (indicating button was clicked)
        if comment_like_form.like.data:
            comment_liked = CommentLikes(user_id=user._id, comment_id=comment._id, like=True, post_id=post._id)
            db.session.add(comment_liked)
            db.session.commit()
            comment.like_count = (len(comment.likes.filter_by(comment_id=comment._id, like=True).all()) -
                               (len(comment.likes.filter_by(comment_id=comment._id, like=False).all())))
            db.session.commit()
            logger.info(
                f"DB: user_id [{user._id}] liked comment_id [{comment._id}]"
            )

        elif comment_like_form.dislike.data:
            comment_liked = CommentLikes(user_id=user._id, comment_id=comment._id, like=False, post_id=post._id)
            db.session.add(comment_liked)
            db.session.commit()
            comment.like_count = (len(comment.likes.filter_by(comment_id=comment._id, like=True).all()) -
                               (len(comment.likes.filter_by(comment_id=comment._id, like=False).all())))
            db.session.commit()
            logger.info(
                f"DB: user_id [{user._id}] disliked comment_id [{comment._id}]"
            )
        return redirect(request.url)
    else:
        comment_like_checker.like = comment_like_form.like.data
        db.session.commit()
        comment.like_count = (len(comment.likes.filter_by(comment_id=comment._id, like=True).all()) -
                              (len(comment.likes.filter_by(comment_id=comment._id, like=False).all())))
        db.session.commit()
        logger.info(
            f"DB: user_id [{user._id}] updated like/dislike on comment_id [{comment._id}]"
        )
        return redirect(request.url)



