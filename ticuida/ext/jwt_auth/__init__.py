"""Autenticação por token JWT (Flask-JWT-Extended) com respostas em português."""

from flask import jsonify
from flask_jwt_extended import JWTManager

jwt = JWTManager()


def init_app(app):
    jwt.init_app(app)


@jwt.user_lookup_loader
def _carregar_usuario(_cabecalho, dados):
    """Disponibiliza o usuário logado em `flask_jwt_extended.current_user`."""
    from ticuida.auth.models import Usuario
    from ticuida.ext.db import db

    usuario = db.session.get(Usuario, int(dados["sub"]))
    return usuario if usuario and usuario.ativo else None


@jwt.user_lookup_error_loader
def _usuario_nao_encontrado(_cabecalho, _dados):
    return jsonify({"erro": "Usuário não encontrado ou inativo."}), 401


@jwt.unauthorized_loader
def _sem_token(_motivo):
    return jsonify({"erro": "Autenticação necessária. Faça login."}), 401


@jwt.invalid_token_loader
def _token_invalido(_motivo):
    return jsonify({"erro": "Token inválido. Faça login novamente."}), 401


@jwt.expired_token_loader
def _token_expirado(_cabecalho, _dados):
    return jsonify({"erro": "Sessão expirada. Faça login novamente."}), 401
