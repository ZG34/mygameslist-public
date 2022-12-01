import re
import inspect
from flask import flash, redirect, url_for, request, Markup

from admintools.loggers import function_logger, logger_setup
from utils import trailing_whitespace_cutter

from app import db, page_not_found
from objects.db_objects.users import Users

logger = logger_setup(__name__, "log.log")


def register_user(form, session):
    function_logger(logger, session, inspect.stack()[0][3], request.referrer)

    if form.validate_on_submit():
        username = form.username.data
        username = trailing_whitespace_cutter(username)

        password = form.password.data
        email = form.email.data
        found_user = Users.query.filter_by(name=username).first()
        found_email = Users.query.filter_by(email=email).first()
        if found_user:
            flash(f"The username {found_user.name} is unavailable", "error")
            logger.info(
                f"registration of [{username}] failed due to name being in use"
            )
            return redirect(url_for("register"))
        elif found_email:
            flash(Markup(f"The email {found_email.email} is already in use. If this is your account, "
                         f"you can recover it <a href='https://127.0.0.1:5000/recovery'>here</a>"))
            logger.info(
                f"registration of [{username}] failed due to email [{email}] being in use"
            )
            return redirect(url_for("register"))
        else:
            regex = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
            if regex.search(username) is None:
                newaccount = Users(username, email, password)
                db.session.add(newaccount)

                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash(f"The username {username} is unavailable", "error")
                    logger.info(
                        f"registration of [{username}] failed due to name being in use"
                    )
                    return redirect(url_for("register"))

                session["user"] = username
                session["email"] = email
                session["user_id"] = newaccount._id
                session.permanent = True

                flash("Registration Successful!", "info")
                logger.info(f"DB: created account. user_id: [{session['user_id']}]")
            else:
                flash("ERROR: Do not use special characters in username", "error")
                logger.warning(f"[{username}] failed at registration due to regex")
                return redirect(request.url)
        return redirect(url_for("home"))


def update_account_info(session, found_user):
    updated_email = request.form.get("email")
    username = request.form.get("user")
    try:
        username = trailing_whitespace_cutter(username)
    except IndexError as e:
        flash(f"Must have a username entered.", "error")
        return redirect(request.url)

    email_checker = Users.query.filter_by(email=updated_email).first()
    if email_checker == found_user:
        pass
    elif email_checker:
        flash(f"The email {updated_email} is already in use.", "error")
        logger.info(
            f"update of [{session['user']}] failed due to email [{updated_email}] being in use"
        )
        return redirect(request.url)

    found_user.email = updated_email
    db.session.commit()
    logger.info(f"DB: user_id:[{session['user_id']}] - updated email address")

    check_if_taken = Users.query.filter_by(name=username).first()
    if len(username) < 1:
        flash("error! new username too short", "info")
    elif (check_if_taken is None) or (check_if_taken == found_user):
        regex = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
        if regex.search(username) is None:
            found_user.name = username
            db.session.commit()
            session["user"] = username
            flash("Edits were saved", "info")
            logger.info(f"DB: user_id:[{session['user_id']}] - updated username")
            return redirect(request.url)
        else:
            logger.warning(
                f"user_id:[{session['user_id']}] - regex failed username change [{username}]"
            )
            flash("Do not use special characters")
            return redirect(request.url)
    else:
        flash("username is taken", "error")
        return redirect(request.url)
