"""Domínio triagem: catálogo de sintomas, registro da triagem e regras de prioridade."""

from .routes import triagem_bp


def init_app(app):
    app.register_blueprint(triagem_bp, url_prefix="/api")
