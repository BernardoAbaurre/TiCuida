"""Domínio unidades: unidades de saúde, convênios aceitos, lotação e recomendação."""

from .routes import convenios_bp, unidades_bp


def init_app(app):
    app.register_blueprint(unidades_bp, url_prefix="/api/unidades")
    app.register_blueprint(convenios_bp, url_prefix="/api/convenios")
