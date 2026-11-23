from flask import Blueprint, jsonify
from flask_jwt_extended import current_user

from ticuida.auth.decorators import papel_requerido
from ticuida.auth.models import PAPEL_PACIENTE
from ticuida.core.validacao import obter_json, validar
from ticuida.pacientes import services
from ticuida.pacientes.schemas import PerfilUpdateIn

pacientes_bp = Blueprint("pacientes", __name__)


@pacientes_bp.get("/me")
@papel_requerido(PAPEL_PACIENTE)
def meu_perfil():
    return jsonify(current_user.paciente.para_dict())


@pacientes_bp.put("/me")
@papel_requerido(PAPEL_PACIENTE)
def atualizar_meu_perfil():
    dados = validar(PerfilUpdateIn, obter_json())
    paciente = services.atualizar_perfil(current_user.paciente, dados)
    return jsonify(paciente.para_dict())
