from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user

from ticuida.auth.decorators import papel_requerido
from ticuida.auth.models import PAPEL_OPERADOR, PAPEL_PACIENTE
from ticuida.core.validacao import obter_json, validar
from ticuida.encaminhamentos import services
from ticuida.encaminhamentos.schemas import EncaminhamentoIn, FilaQuery, StatusIn

encaminhamentos_bp = Blueprint("encaminhamentos", __name__)


@encaminhamentos_bp.post("")
@papel_requerido(PAPEL_PACIENTE)
def estou_indo():
    """ "Estou indo": envia a pré-triagem para a fila da unidade e gera o protocolo."""
    dados = validar(EncaminhamentoIn, obter_json())
    encaminhamento = services.criar_encaminhamento(
        current_user.paciente, dados.triagem_id, dados.unidade_id
    )
    return jsonify(encaminhamento.para_dict_paciente()), 201


@encaminhamentos_bp.get("/meus")
@papel_requerido(PAPEL_PACIENTE)
def meus_encaminhamentos():
    return jsonify(
        [e.para_dict_paciente() for e in services.listar_do_paciente(current_user.paciente)]
    )


@encaminhamentos_bp.get("/fila")
@papel_requerido(PAPEL_OPERADOR)
def fila():
    filtro = validar(FilaQuery, request.args.to_dict())
    itens = services.fila_da_unidade(current_user, filtro.status)
    return jsonify(
        {
            "unidade": {"id": current_user.unidade.id, "nome": current_user.unidade.nome},
            "encaminhamentos": [e.para_dict_operador() for e in itens],
        }
    )


@encaminhamentos_bp.get("/<int:encaminhamento_id>")
@papel_requerido(PAPEL_OPERADOR)
def detalhar(encaminhamento_id: int):
    return jsonify(services.obter_da_unidade(current_user, encaminhamento_id).para_dict_operador())


@encaminhamentos_bp.patch("/<int:encaminhamento_id>")
@papel_requerido(PAPEL_OPERADOR)
def atualizar_status(encaminhamento_id: int):
    dados = validar(StatusIn, obter_json())
    encaminhamento = services.atualizar_status(current_user, encaminhamento_id, dados.status)
    return jsonify(encaminhamento.para_dict_operador())
