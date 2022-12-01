from flask import (
    Blueprint,
    request,
    session,
    flash,
    render_template,
    redirect,
    url_for,
    g,
)
from sqlalchemy import func
from flask_bcrypt import generate_password_hash

from app import app, db, page_not_found, csrf
from utils import login_required
from admintools.loggers import routing_logger, logger_setup
from blueprints.users.utils import register_user, update_account_info
from blueprints.users.email import send_recovery_email

from objects.forms import RecoveryForm, RegistrationForm

from objects.db_objects.users import Users, check_pw
from objects.db_objects.posts import Posts
from objects.db_objects.users_games import UsersGames
from objects.db_objects.post_likes import PostLikes


users_bp = Blueprint(
    "users_bp", __name__, template_folder="templates", static_folder="static"
)

logger = logger_setup(__name__, "log.log")

# FIXME why is routing and pointing working when route uses app but points based on blueprint?
#  because templates is still nearest target?


@app.route("/login", methods=["POST", "GET"])
def login():
    routing_logger(logger, session, request.environ)

    csrf.generate_new_token()

    if request.method == "POST":
        session.permanent = True
        username = request.form["name"]
        password = request.form["pw"]

        found_user = Users.query.filter(func.lower(Users.name) == username.lower()).first()
        if found_user:
            if check_pw(username, password):
                session["email"] = found_user.email
                session["user"] = found_user.name
                session["user_id"] = found_user._id
                g.user = found_user.name
                flash("login successful!", "info")
                logger.info(f"user_id:[{session['user_id']}] logged in")
                return redirect(url_for("home"))
            else:
                g.user = None
                flash("login failed", "error")
                logger.warning(
                    f"login failed bad password, user_id attempted: {found_user._id}"
                )
                render_template("login.html")
        else:
            flash("login failed", "error")
            logger.warning(f"login failed, username INVALID")
            render_template("login.html")
    else:
        if "user" in session:
            logger.error(f"a user attempted to log in while a session was underway")
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    routing_logger(logger, session, request.environ)
    # TODO confirmation email, to ensure emails dont get tied up by non-owners

    form = RegistrationForm()
    if request.method == "POST":
        # print(request.values)
        return register_user(form=form, session=session)
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    routing_logger(logger, session, request.environ)

    logger.info(f"logging out user_id: {session['user_id']}")
    session.pop("user", None)
    session.pop("user_id", None)
    session.pop("email", None)
    session.pop("category", None)
    flash("You have been logged out", "info")
    if "user_id" not in session:
        logger.info(f"logout complete")
    else:
        logger.error(f"{session['user_id']} logout failed")
    return redirect(request.url)


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    routing_logger(logger, session, request.environ)

    username = session["user"]
    found_user = Users.query.filter_by(name=username).first()
    email = found_user.email
    if request.method == "POST":
        if 'delete' in request.form.keys():
            logger.info(f"DB: Deleting account: [{found_user._id}]")
            db.session.query(Users).filter(Users._id == found_user._id).delete()
            db.session.commit()
            flash("Account has been deleted!", "info")
            return redirect(url_for('logout'))

        elif 'user' in request.form.keys():
            return update_account_info(session=session, found_user=found_user)

    return render_template(
        "account.html", username=username, email=email, user=found_user
    )


@app.route("/profile/<path:username>", methods=["POST", "GET"])
def profile(username):
    routing_logger(logger, session, request.environ)

    user_getter = Users.query.filter_by(name=username).first()
    if user_getter is None:
        return page_not_found(user_getter)

    username = user_getter.name
    user_posts = Posts.query.filter_by(user_id=user_getter._id).all()

    num_posts = len(user_getter.posts)
    num_comments = len(user_getter.comments)
    num_likes = len(PostLikes.query.filter_by(user_id=user_getter._id, like=1).all())
    num_games = len(user_getter.games.all())
    num_suggestions = len(user_getter.similar)

    completed_games = len(UsersGames.query.filter_by(user_id=user_getter._id, status='completed').all())
    want_to_play_games = len(UsersGames.query.filter_by(user_id=user_getter._id, status='want to play').all())
    playing_games = len(UsersGames.query.filter_by(user_id=user_getter._id, status='playing').all())
    dropped_games = len(UsersGames.query.filter_by(user_id=user_getter._id, status='dropped').all())
    all_ratings = UsersGames.query.with_entities(UsersGames.score).filter_by(user_id=user_getter._id).all()
    all_ratings = [int(x[0]) for x in all_ratings if x[0] is not None]

    try:
        average_rating = sum(all_ratings) / len(all_ratings)
    except ZeroDivisionError as e:
        average_rating = None

    return render_template(
        "profile.html",
        username=username,
        user_posts=user_posts,
        user=user_getter,
        num_posts=num_posts,
        num_comments=num_comments,
        num_likes=num_likes,
        num_games=num_games,
        completed_games=completed_games,
        want_to_play_games=want_to_play_games,
        playing_games=playing_games,
        dropped_games=dropped_games,
        average_rating=average_rating,
        num_suggestions=num_suggestions
    )


@app.route("/recovery", methods=["POST", "GET"])
def recovery():
    routing_logger(logger, session, request.environ)

    form = RecoveryForm()

    if form.validate_on_submit():
        recipient = form.email.data

        email_checker = Users.query.filter_by(email=recipient).first()
        if email_checker:
            flash(f"Sent recovery email to {recipient} if tied to an account")
            send_recovery_email(recipient, user=email_checker)
            logger.info(f"recovery email sent to [{recipient}]")
        else:
            flash(f"Sent recovery email to {recipient} if tied to an account")

    return render_template("recovery.html", form=form)


@app.route("/reset/<token>", methods=["POST", "GET"])
def reset(token):
    routing_logger(logger, session, request.environ)

    user = Users.verify_reset_token(token)
    if not user:
        logger.critical('recovery link accessed via external email failed')
        print('no user found')
        return redirect(url_for('login'))

    else:
        if request.method == 'POST':
            password = request.form['password']
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            logger.info(f"DB: changed password for user_id: [{user._id}]")
            flash('Password updated!')
            return redirect(url_for('login'))

        return render_template('reset.html', user=user)


@app.route("/privacypolicy")
def privacy_policy():
    routing_logger(logger, session, request.environ)
    return render_template('privacypolicy.html')