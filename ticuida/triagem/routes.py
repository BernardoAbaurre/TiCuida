from flask import Blueprint, jsonify
from flask_jwt_extended import current_user

from ticuida.auth.decorators import papel_requerido
from ticuida.auth.models import PAPEL_PACIENTE
from ticuida.core.validacao import obter_json, validar
from ticuida.triagem import regras, services
from ticuida.triagem.schemas import TriagemIn

triagem_bp = Blueprint("triagem", __name__)


@triagem_bp.get("/sintomas")
def listar_sintomas():
    """Catálogo público de sintomas (os sinais de alarme vêm marcados)."""
    return jsonify([s.para_dict() for s in services.listar_sintomas()])


@triagem_bp.post("/triagens")
@papel_requerido(PAPEL_PACIENTE)
def registrar_triagem():
    dados = validar(TriagemIn, obter_json())
    triagem, resultado = services.registrar_triagem(current_user.paciente, dados)
    return (
        jsonify(
            {
                "triagem": triagem.para_dict(),
                "prioridade": resultado.prioridade,
                "emergencia": resultado.emergencia,
                "motivos": resultado.motivos,
                "orientacao": resultado.orientacao,
            }
        ),
        201,
    )


@triagem_bp.get("/triagens")
@papel_requerido(PAPEL_PACIENTE)
def listar_minhas_triagens():
    return jsonify([t.para_dict() for t in current_user.paciente.triagens])


@triagem_bp.get("/triagens/<int:triagem_id>")
@papel_requerido(PAPEL_PACIENTE)
def detalhar_triagem(triagem_id: int):
    triagem = services.obter_triagem_do_paciente(current_user.paciente, triagem_id)
    return jsonify({**triagem.para_dict(), "orientacao": regras.ORIENTACOES[triagem.prioridade]})
