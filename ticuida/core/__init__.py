"""Núcleo: utilitários compartilhados (tempo, validação, CPF) e rota de saúde."""

from .routes import core_bp


def init_app(app):
    app.register_blueprint(core_bp, url_prefix="/api")
