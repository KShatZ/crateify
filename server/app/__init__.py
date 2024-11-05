from flask import Flask
from os import getenv

from .middleware.auth import login_manager


def create_app():
    """Initializes and returns a Flask Application Object.

    :return: app
    :rtype: Flask Application
    """

    app = Flask("__name__")

    with app.app_context():

        # ------ User Authentication & Session Management ------ #
        login_manager.init_app(app)
        # TODO: This along with other envs should be passed into create_app (manage different envs better)
        app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY", "someSecretKey") # eventually rotate values

        # ------ Blueprint Registration ------ #
        from .handlers.authentication import Authentication
        app.register_blueprint(Authentication)
        from .handlers.user import User
        app.register_blueprint(User)


        return app
