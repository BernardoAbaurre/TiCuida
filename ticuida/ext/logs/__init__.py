"""Logging: console + arquivo rotativo em LOG_DIR.

O logger da aplicação se chama "ticuida" (é o `app.logger`), e os módulos usam
`logging.getLogger(__name__)`, que herdam esses handlers. Por causa da LGPD,
não registramos CPF, sintomas ou outros dados de saúde: apenas IDs.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import request
from flask.logging import default_handler

FORMATO = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def init_app(app):
    logger = logging.getLogger("ticuida")
    logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    logger.removeHandler(default_handler)
    for handler in list(logger.handlers):  # evita duplicar ao recriar o app (testes)
        logger.removeHandler(handler)

    formatador = logging.Formatter(FORMATO)

    console = logging.StreamHandler()
    console.setFormatter(formatador)
    logger.addHandler(console)

    pasta = app.config.get("LOG_DIR")
    if pasta:
        Path(pasta).mkdir(parents=True, exist_ok=True)
        arquivo = RotatingFileHandler(
            Path(pasta) / "ticuida.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        arquivo.setFormatter(formatador)
        logger.addHandler(arquivo)

    logger.propagate = False

    @app.after_request
    def _registrar_requisicao(resposta):
        if request.path.startswith("/api") and request.path != "/api/health":
            nivel = logging.WARNING if resposta.status_code >= 400 else logging.INFO
            logger.log(nivel, "%s %s -> %s", request.method, request.path, resposta.status_code)
        return resposta
