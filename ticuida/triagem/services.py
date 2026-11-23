import logging

from sqlalchemy import select

from ticuida.errors import APIError
from ticuida.ext.db import db
from ticuida.pacientes.models import Paciente
from ticuida.triagem import regras
from ticuida.triagem.models import Sintoma, Triagem
from ticuida.triagem.schemas import TriagemIn

logger = logging.getLogger(__name__)


def listar_sintomas() -> list[Sintoma]:
    consulta = select(Sintoma).where(Sintoma.ativo).order_by(Sintoma.sinal_alarme, Sintoma.nome)
    return list(db.session.scalars(consulta))


def registrar_triagem(
    paciente: Paciente, dados: TriagemIn
) -> tuple[Triagem, regras.ResultadoTriagem]:
    sintomas = []
    if dados.sintomas:
        sintomas = list(
            db.session.scalars(select(Sintoma).where(Sintoma.id.in_(dados.sintomas), Sintoma.ativo))
        )
        if len(sintomas) != len(dados.sintomas):
            raise APIError(
                422, "Dados inválidos.", campos={"sintomas": ["Há sintomas inválidos na lista."]}
            )

    resultado = regras.classificar(
        regras.DadosTriagem(
            tem_sinal_alarme=any(s.sinal_alarme for s in sintomas),
            intensidade=dados.intensidade,
            idade=paciente.idade,
            inicio_sintomas=dados.inicio_sintomas,
            temperatura=dados.temperatura,
        )
    )

    triagem = Triagem(
        paciente=paciente,
        queixa_principal=dados.queixa_principal,
        intensidade=dados.intensidade,
        inicio_sintomas=dados.inicio_sintomas,
        temperatura=dados.temperatura,
        prioridade=resultado.prioridade,
        sintomas=sintomas,
    )
    db.session.add(triagem)
    db.session.commit()
    logger.info("Triagem %s registrada com prioridade %s", triagem.id, triagem.prioridade)
    return triagem, resultado


def obter_triagem_do_paciente(paciente: Paciente, triagem_id: int) -> Triagem:
    triagem = db.session.get(Triagem, triagem_id)
    if not triagem or triagem.paciente_id != paciente.id:
        raise APIError(404, "Triagem não encontrada.")
    return triagem
