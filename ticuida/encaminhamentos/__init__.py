"""Domínio encaminhamentos: "Estou indo", protocolo e fila da unidade."""

from .routes import encaminhamentos_bp


def init_app(app):
    app.register_blueprint(encaminhamentos_bp, url_prefix="/api/encaminhamentos")
