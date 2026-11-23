from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required

from ticuida.auth import services
from ticuida.auth.schemas import CadastroPacienteIn, LoginIn
from ticuida.core.validacao import obter_json, validar

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/cadastro")
def cadastro():
    """Cadastra um paciente e já devolve o token de acesso."""
    dados = validar(CadastroPacienteIn, obter_json())
    usuario = services.cadastrar_paciente(dados)
    return jsonify({"token": services.gerar_token(usuario), "usuario": usuario.para_dict()}), 201


@auth_bp.post("/login")
def login():
    dados = validar(LoginIn, obter_json())
    usuario = services.autenticar(dados.email, dados.senha)
    return jsonify({"token": services.gerar_token(usuario), "usuario": usuario.para_dict()})


@auth_bp.get("/me")
@jwt_required()
def me():
    return jsonify(current_user.para_dict())
