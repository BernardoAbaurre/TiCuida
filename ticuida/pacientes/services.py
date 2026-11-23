import logging

from ticuida.errors import APIError
from ticuida.ext.db import db
from ticuida.pacientes.models import Paciente
from ticuida.pacientes.schemas import PerfilUpdateIn
from ticuida.unidades.models import Convenio

logger = logging.getLogger(__name__)

CAMPOS_OBRIGATORIOS = {"telefone", "contato_emergencia_nome", "contato_emergencia_telefone"}


def atualizar_perfil(paciente: Paciente, dados: PerfilUpdateIn) -> Paciente:
    alteracoes = dados.model_dump(include=dados.model_fields_set)

    vazios = {
        campo for campo in CAMPOS_OBRIGATORIOS if campo in alteracoes and not alteracoes[campo]
    }
    if vazios:
        raise APIError(422, "Dados inválidos.", campos={c: ["Campo obrigatório."] for c in vazios})

    if "convenio_id" in alteracoes:
        convenio = db.session.get(Convenio, alteracoes["convenio_id"] or 0)
        if not convenio or not convenio.ativo:
            raise APIError(422, "Dados inválidos.", campos={"convenio_id": ["Convênio inválido."]})

    for campo, valor in alteracoes.items():
        setattr(paciente, campo, valor or None if campo == "numero_carteirinha" else valor)
    db.session.commit()
    logger.info("Perfil do paciente %s atualizado (%s)", paciente.id, ", ".join(sorted(alteracoes)))
    return paciente
