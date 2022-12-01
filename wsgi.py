import logging

from flask_msearch import Search

from app import app, db
from admintools.adminhandler import admin_views

from blueprints.users.routes import users_bp
from blueprints.posts.routes import posts_bp
from blueprints.main.routes import main_bp
from blueprints.games.routes import games_bp

app.register_blueprint(users_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(main_bp)
app.register_blueprint(games_bp)

admin_views()

search = Search()
search.init_app(app)

logging.getLogger("werkzeug").setLevel(logging.INFO)

if __name__ == "__main__":
    db.create_all()

    app.run(debug=True, ssl_context='adhoc')
    # app.run()
