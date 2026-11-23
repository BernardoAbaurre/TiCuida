import logging
import secrets

from sqlalchemy import select

from ticuida.auth.models import Usuario
from ticuida.encaminhamentos.models import STATUS_ATIVOS, TRANSICOES, Encaminhamento
from ticuida.errors import APIError
from ticuida.ext.db import db
from ticuida.pacientes.models import Paciente
from ticuida.triagem.regras import EMERGENCIA, ORDEM_PRIORIDADE
from ticuida.triagem.services import obter_triagem_do_paciente
from ticuida.unidades.services import obter_unidade

logger = logging.getLogger(__name__)

# Sem 0/O e 1/I para o protocolo ser fácil de ditar na recepção
ALFABETO_PROTOCOLO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TAMANHO_PROTOCOLO = 8


def gerar_protocolo() -> str:
    for _ in range(10):
        protocolo = "".join(secrets.choice(ALFABETO_PROTOCOLO) for _ in range(TAMANHO_PROTOCOLO))
        if not db.session.scalar(
            select(Encaminhamento.id).where(Encaminhamento.protocolo == protocolo)
        ):
            return protocolo
    raise APIError(500, "Não foi possível gerar o protocolo. Tente novamente.")


def criar_encaminhamento(paciente: Paciente, triagem_id: int, unidade_id: int) -> Encaminhamento:
    triagem = obter_triagem_do_paciente(paciente, triagem_id)
    if triagem.prioridade == EMERGENCIA:
        raise APIError(
            422,
            "Em caso de emergência, ligue para o SAMU (192) ou vá à emergência mais próxima.",
        )
    if triagem.encaminhamento:
        raise APIError(409, "Esta triagem já foi enviada para uma unidade.")

    unidade = obter_unidade(unidade_id)
    if not unidade.aceita_convenio(paciente.convenio_id):
        raise APIError(
            422,
            "Dados inválidos.",
            campos={"unidade_id": ["Esta unidade não aceita o seu convênio."]},
        )

    encaminhamento = Encaminhamento(triagem=triagem, unidade=unidade, protocolo=gerar_protocolo())
    db.session.add(encaminhamento)
    db.session.commit()
    logger.info(
        "Encaminhamento %s criado (triagem %s -> unidade %s)",
        encaminhamento.id,
        triagem.id,
        unidade.id,
    )
    return encaminhamento


def listar_do_paciente(paciente: Paciente) -> list[Encaminhamento]:
    return [t.encaminhamento for t in paciente.triagens if t.encaminhamento]


def fila_da_unidade(operador: Usuario, filtro: str = "ativos") -> list[Encaminhamento]:
    """Pré-triagens da unidade do operador, por prioridade e depois por horário.

    LGPD: o operador só enxerga encaminhamentos da própria unidade.
    """
    consulta = select(Encaminhamento).where(Encaminhamento.unidade_id == operador.unidade_id)
    if filtro == "ativos":
        consulta = consulta.where(Encaminhamento.status.in_(STATUS_ATIVOS))
    elif filtro != "todos":
        consulta = consulta.where(Encaminhamento.status == filtro)

    encaminhamentos = db.session.scalars(consulta)
    return sorted(
        encaminhamentos,
        key=lambda e: (ORDEM_PRIORIDADE[e.triagem.prioridade], e.criado_em, e.id),
    )


def obter_da_unidade(operador: Usuario, encaminhamento_id: int) -> Encaminhamento:
    encaminhamento = db.session.get(Encaminhamento, encaminhamento_id)
    # 404 (e não 403) para não revelar a existência de dados de outra unidade
    if not encaminhamento or encaminhamento.unidade_id != operador.unidade_id:
        raise APIError(404, "Encaminhamento não encontrado.")
    return encaminhamento


def atualizar_status(operador: Usuario, encaminhamento_id: int, novo_status: str) -> Encaminhamento:
    encaminhamento = obter_da_unidade(operador, encaminhamento_id)
    if novo_status not in TRANSICOES[encaminhamento.status]:
        raise APIError(
            409,
            f"Não é possível mudar o status de '{encaminhamento.status}' para '{novo_status}'.",
        )
    anterior = encaminhamento.status
    encaminhamento.status = novo_status
    db.session.commit()
    logger.info(
        "Encaminhamento %s: %s -> %s (operador %s)",
        encaminhamento.id,
        anterior,
        novo_status,
        operador.id,
    )
    return encaminhamento
