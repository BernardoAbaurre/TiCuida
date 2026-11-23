"""Domínio pacientes: perfil e convênio do paciente."""

from .routes import pacientes_bp


def init_app(app):
    app.register_blueprint(pacientes_bp, url_prefix="/api/pacientes")
