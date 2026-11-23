"""CORS liberado só para as origens do front-end configuradas no .env."""

from flask_cors import CORS

cors = CORS()


def init_app(app):
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
