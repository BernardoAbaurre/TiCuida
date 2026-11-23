"""Domínio auth: cadastro, login, papéis (paciente/operador) e usuário logado."""

from .routes import auth_bp


def init_app(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
