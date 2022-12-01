import os
from datetime import timedelta

import humanize
from flask_admin.contrib import sqla
from sqlalchemy import create_engine, event, text
from flask import Flask, render_template, request, redirect, session, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from sqlalchemy.pool import StaticPool

from admintools.loggers import logger_setup, routing_logger, function_logger

logger = logger_setup(__name__, "log.log")


def page_not_found(e):
    logger.error(f"user_id:[{session['user_id'] if 'user_id' in session else None}] "
                 f"404 error "
                 f"ROUTING: target "
                 f"[{request.environ.get('RAW_URI')}] - accessed via: "
                 f"[{request.environ.get('HTTP_REFERER', 'external')}]"
                 )
    return render_template('404.html'), 404


app = Flask(__name__)
app.secret_key = "whateveryouwantittobe"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
ENGINE = create_engine('sqlite:///users.sqlite3',
                       echo=False)
                       # connect_args={"check_same_thread": False},
                       # poolclass=StaticPool)
connection = ENGINE.raw_connection()
cursor = connection.cursor()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.getcwd() + '/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.filters['humanize'] = humanize.naturaltime


def escape_html(obj):
    if '<' in obj:
        new_obj = obj.replace('<', ' < ')
        return new_obj
    else:
        return obj


app.jinja_env.filters['escape'] = escape_html

app.permanent_session_lifetime = timedelta(hours=5)

app.register_error_handler(404, page_not_found)


@event.listens_for(ENGINE, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # cursor.execute("PRAGMA journal_mode=begin-concurrent")
    # cursor.execute("PRAGMA journal_mode=WAL2")
    cursor.execute("PRAGMA journal_mode=WAL")

    cursor.close()


set_sqlite_pragma(connection, db)

""" used to force https. currently breaking some stuff. if using then removing, must clear cached cookies + images
    whenever this is running, must change broken script tags to https. """


# @app.before_request
# def before_request():
#     if not request.is_secure:
#         url = request.url.replace('http://', 'https://', 1)
#         code = 301
#         return redirect(url, code=code)


csrf = SeaSurf()
csrf.init_app(app)

csrf._csrf_secure = True
csrf._csrf_httponly = True
csrf._csrf_samesite = 'STRICT'
csrf._csrf_name = '__Secure-_csrf_token'
# app.SESSION_COOKIE_SECURE = True

# todo make sure img sources are all safe
csp = {
    'default-src': " 'none' ",
    'script-src': " 'strict-dynamic' ",
    'style-src-elem': " 'self' https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css https://ajax.googleapis.com https://cdn.jsdelivr.net/npm/@yaireo/tagify/dist/tagify.css https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.3/dist/css/splide.min.css",
    'img-src': " * about: data: 'self' https://encrypted-tbn0.gstatic.com/images https://www.w3.org ",
    'style-src': " 'self' https://cdn.jsdelivr.net/npm/@yaireo/tagify/dist/tagify.css https://cdn.jsdelivr.net/npm/@splidejs/splide@4.1.3/dist/css/splide.min.css",
    'base-uri': " 'none' ",
    'form-action': " 'self' ",
    'frame-ancestors': " 'self' "
}

ONE_YEAR_IN_SECS = 31556926

talisman = Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
    frame_options='SAMEORIGIN',
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_include_subdomains=True,
    strict_transport_security_max_age=ONE_YEAR_IN_SECS,
    x_content_type_options=True,
    x_xss_protection=True,
    session_cookie_samesite='STRICT',
    session_cookie_secure=True,
    # permissions_policy=['geolocation=()', 'camera=()']
)

csrf.exempt_urls('/admin')

if __name__ == "__main__":
    app.run()
