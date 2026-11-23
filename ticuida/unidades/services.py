"""Regras de negócio das unidades: recomendação por convênio, lotação e distância."""

import logging
import math
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import select

from ticuida.auth.models import Usuario
from ticuida.core.tempo import agora, iso, minutos_desde
from ticuida.errors import APIError
from ticuida.ext.db import db
from ticuida.unidades.models import Convenio, RegistroLotacao, Unidade

logger = logging.getLogger(__name__)

RAIO_TERRA_KM = 6371.0
# Unidade sem lotação informada fica depois de "alta": não sabemos se está cheia
ORDEM_LOTACAO = {"baixa": 0, "media": 1, "alta": 2, None: 3}


def distancia_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distância em linha reta entre dois pontos (fórmula de Haversine)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * RAIO_TERRA_KM * math.asin(math.sqrt(a))


def listar_convenios() -> list[Convenio]:
    return list(db.session.scalars(select(Convenio).where(Convenio.ativo).order_by(Convenio.nome)))


def obter_unidade(unidade_id: int) -> Unidade:
    unidade = db.session.get(Unidade, unidade_id)
    if not unidade or not unidade.ativo:
        raise APIError(404, "Unidade não encontrada.")
    return unidade


def lotacao_atual(unidade_id: int) -> RegistroLotacao | None:
    return db.session.scalar(
        select(RegistroLotacao)
        .where(RegistroLotacao.unidade_id == unidade_id)
        .order_by(RegistroLotacao.registrado_em.desc(), RegistroLotacao.id.desc())
        .limit(1)
    )


def resumo_lotacao(
    registro: RegistroLotacao | None, referencia: datetime | None = None
) -> dict | None:
    if registro is None:
        return None
    return {
        "nivel": registro.nivel,
        "atualizado_em": iso(registro.registrado_em),
        "minutos_desde_atualizacao": minutos_desde(registro.registrado_em, referencia),
    }


def detalhar_unidade(unidade: Unidade, momento: datetime | None = None) -> dict:
    momento = momento or agora()
    horario_local = momento.astimezone(ZoneInfo(current_app.config["FUSO_HORARIO"])).time()
    return {
        **unidade.para_dict(),
        "aberta_agora": unidade.aberta_em(horario_local),
        "lotacao": resumo_lotacao(lotacao_atual(unidade.id), momento),
    }


def recomendar_unidades(
    convenio_id: int | None,
    lat: float | None = None,
    lng: float | None = None,
    momento: datetime | None = None,
) -> list[dict]:
    """Unidades ativas que aceitam o convênio, ordenadas por:
    1) abertas antes de fechadas; 2) lotação (baixa → alta → sem informação);
    3) distância, quando a localização do paciente é conhecida.
    """
    consulta = select(Unidade).where(Unidade.ativo)
    if convenio_id is not None:
        consulta = consulta.where(Unidade.convenios.any(Convenio.id == convenio_id))

    resultado = []
    for unidade in db.session.scalars(consulta):
        item = detalhar_unidade(unidade, momento)
        item["distancia_km"] = (
            round(distancia_km(lat, lng, unidade.latitude, unidade.longitude), 1)
            if lat is not None and lng is not None
            else None
        )
        resultado.append(item)

    def chave(item: dict):
        nivel = item["lotacao"]["nivel"] if item["lotacao"] else None
        distancia = item["distancia_km"] if item["distancia_km"] is not None else math.inf
        return (not item["aberta_agora"], ORDEM_LOTACAO[nivel], distancia, item["nome"])

    return sorted(resultado, key=chave)


def registrar_lotacao(operador: Usuario, unidade_id: int, nivel: str) -> RegistroLotacao:
    unidade = obter_unidade(unidade_id)
    if operador.unidade_id != unidade.id:
        raise APIError(403, "Você só pode atualizar a lotação da sua unidade.")
    registro = RegistroLotacao(unidade=unidade, operador=operador, nivel=nivel)
    db.session.add(registro)
    db.session.commit()
    logger.info(
        "Lotação da unidade %s atualizada para %s (operador %s)", unidade.id, nivel, operador.id
    )
    return registro
