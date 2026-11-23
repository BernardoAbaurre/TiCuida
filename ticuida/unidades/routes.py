from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ticuida.auth.decorators import papel_requerido
from ticuida.auth.models import PAPEL_OPERADOR
from ticuida.core.validacao import obter_json, validar
from ticuida.unidades import services
from ticuida.unidades.schemas import LotacaoIn, RecomendacaoQuery

unidades_bp = Blueprint("unidades", __name__)
convenios_bp = Blueprint("convenios", __name__)


@convenios_bp.get("")
def listar_convenios():
    """Público: usado no formulário de cadastro."""
    return jsonify([c.para_dict() for c in services.listar_convenios()])


@unidades_bp.get("")
@jwt_required()
def recomendar():
    """Unidades compatíveis com o convênio, ordenadas por lotação e distância.

    Para o paciente, o convênio padrão é o do próprio perfil.
    """
    filtros = validar(RecomendacaoQuery, request.args.to_dict())
    convenio_id = filtros.convenio_id
    if convenio_id is None and current_user.eh_paciente:
        convenio_id = current_user.paciente.convenio_id
    unidades = services.recomendar_unidades(convenio_id, filtros.lat, filtros.lng)
    return jsonify({"convenio_id": convenio_id, "unidades": unidades})


@unidades_bp.get("/<int:unidade_id>")
@jwt_required()
def detalhar(unidade_id: int):
    return jsonify(services.detalhar_unidade(services.obter_unidade(unidade_id)))


@unidades_bp.post("/<int:unidade_id>/lotacao")
@papel_requerido(PAPEL_OPERADOR)
def registrar_lotacao(unidade_id: int):
    dados = validar(LotacaoIn, obter_json())
    registro = services.registrar_lotacao(current_user, unidade_id, dados.nivel)
    return jsonify(services.resumo_lotacao(registro)), 201
