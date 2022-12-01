import re

from flask import Blueprint, request, session, flash, render_template, redirect
from sqlalchemy import text

from app import app, page_not_found, db
from utils import login_required
from admintools.loggers import routing_logger, logger_setup
from blueprints.posts.utils import new_post_poster, reply_poster, post_like_updater, comment_like_updater
from objects.forms import PostForm, ReplyForm, LikeForm, ForumFilterForm, LikeForm2

from objects.db_objects.posts import Posts
from objects.db_objects.users import Users
from objects.db_objects.comments import Comments
from objects.db_objects.comment_likes import CommentLikes
from objects.db_objects.post_likes import PostLikes
from objects.db_objects.post_games import PostGames
from objects.db_objects.games import Games

posts_bp = Blueprint(
    "posts_bp", __name__, template_folder="templates", static_folder="static"
)

logger = logger_setup(__name__, "log.log")


@app.route("/forums")
def forums():
    routing_logger(logger, session, request.environ)
    page = request.args.get("page", 1, type=int)

    form = ForumFilterForm(request.args)
    posts = Posts.query.order_by(text("id desc")).paginate(page, 9, False)

    if form.sort.data:
        selector = form.selector.data
        order_by = form.order_by.data
        if selector == "Date Posted" and order_by == "DESC":
            posts = Posts.query.order_by(text("id desc")).paginate(page, 9, False)
        if selector == "Date Posted" and order_by == "ASC":
            posts = Posts.query.order_by(text("id asc")).paginate(page, 9, False)
        if selector == "Likes" and order_by == "DESC":
            posts = Posts.query.order_by(text("like_count desc")).paginate(page, 9, False)
        if selector == "Likes" and order_by == "ASC":
            posts = Posts.query.order_by(text("like_count asc")).paginate(page, 9, False)

    return render_template("forums.html", posts=posts.items, form=form, pages=posts)


@app.route("/newpost/<path:game_name>", methods=["POST", "GET"])
@app.route("/newpost", methods=["POST", "GET"])
@login_required
def new_post(game_name=None):
    routing_logger(logger, session, request.environ)
    form = PostForm()
    username = session["user"]
    if form.validate_on_submit():
        return new_post_poster(session=session, form=form, username=username)

    return render_template("newpost.html", form=form, game_name=game_name if game_name else None)


@app.route("/forums/<path:post_name>", methods=["GET", "POST"])
def view_post(post_name):
    routing_logger(logger, session, request.environ)
    post_like_form = LikeForm()
    comment_like_form = LikeForm2()  # TODO must make distinct form. cant repeat exact.
    reply_form = ReplyForm()
    comment_sort_form = ForumFilterForm(request.args)

    post = Posts.query.filter_by(title=post_name).first()
    if post is None:
        return page_not_found(post)

    comments = Comments.query.filter_by(post_id=post._id).order_by(text("id desc")).all()

    post_likes_total = post.like_count
    postgames = PostGames.query.filter_by(post_id=post._id).all()
    linked_games = []
    for line in postgames:
        game = Games.query.filter_by(_id=line.game_id).first()
        linked_games.append(game)

    if request.method == "GET" and comment_sort_form.sort.data:
        selector = comment_sort_form.selector.data
        order_by = comment_sort_form.order_by.data
        if selector == "Date Posted" and order_by == "DESC":
            comments = Comments.query.filter_by(post_id=post._id).order_by(text("id desc")).all()
        if selector == "Date Posted" and order_by == "ASC":
            comments = Comments.query.filter_by(post_id=post._id).order_by(text("id asc")).all()
        if selector == "Likes" and order_by == "DESC":
            comments = Comments.query.filter_by(post_id=post._id).order_by(text("like_count desc")).all()
        if selector == "Likes" and order_by == "ASC":
            comments = Comments.query.filter_by(post_id=post._id).order_by(text("like_count asc")).all()

    if "user" in session:
        username = session["user"]
        user = Users.query.filter_by(name=username).first()
        logger.info(f"user_id [{user._id}] viewing post_id [{post._id}]")
        post_like_checker = PostLikes.query.filter_by(user_id=user._id, post_id=post._id).first()

        if request.method == "POST":
            if request.form.get('delete') == 'comment-delete':
                comment = Comments.query.filter_by(_id=request.form.get('commentid')).first()
                logger.info(f"DB: user_id:[{session['user_id']} deleting comment comment_id:[{comment._id}]")

                db.session.query(Comments).filter(Comments._id == comment._id).delete()
                db.session.commit()
                flash("Comment has been deleted!", "info")

                return redirect(request.url)

            if request.form.get('like') == 'CommentLike' or request.form.get('dislike') == 'CommentDislike':
                comment = Comments.query.filter_by(_id=request.form.get('commentid')).first()
                comment_like_checker = CommentLikes.query.filter_by(user_id=user._id, comment_id=comment._id).first()
                return comment_like_updater(comment_like_checker=comment_like_checker, user=user, comment=comment,
                                            comment_like_form=comment_like_form, session=session, post=post)

            if reply_form.validate_on_submit():
                return reply_poster(reply_form=reply_form, user=user, post=post, session=session)

            if post_like_form.is_submitted():
                return post_like_updater(post_like_checker=post_like_checker, user=user, post=post,
                                         post_like_form=post_like_form, session=session)

        return render_template("viewpost.html", post=post, reply_form=reply_form, comments=comments,
                               post_like_form=post_like_form, post_like_checker=post_like_checker,
                               post_likes_total=post_likes_total, linked_games=linked_games,
                               comment_sort_form=comment_sort_form, comment_like_form=comment_like_form, user=user)

    else:
        flash("Create an account / login to post a reply.", "info")

    return render_template("viewpost.html", post=post, reply_form=reply_form, comments=comments,
                           post_like_form=post_like_form, post_likes_total=post_likes_total,
                           linked_games=linked_games, comment_sort_form=comment_sort_form,
                           comment_like_form=comment_like_form)
