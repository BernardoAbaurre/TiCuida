import logging

from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ticuida.core.tempo import agora, iso
from ticuida.ext.db import db

logger = logging.getLogger(__name__)

core_bp = Blueprint("core", __name__)


@core_bp.get("/health")
def health():
    """Verifica se a API e o banco estão respondendo."""
    try:
        db.session.execute(text("SELECT 1"))
        banco = "ok"
    except SQLAlchemyError:
        logger.exception("Banco de dados indisponível no health check")
        banco = "indisponivel"
    status = 200 if banco == "ok" else 503
    return (
        jsonify(
            {"status": "ok" if status == 200 else "erro", "banco": banco, "horario": iso(agora())}
        ),
        status,
    )
