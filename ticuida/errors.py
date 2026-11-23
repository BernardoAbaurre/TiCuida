"""Erros da API e handlers que sempre respondem JSON em português."""

import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

_MENSAGENS_HTTP = {
    400: "Requisição inválida.",
    401: "Autenticação necessária.",
    403: "Acesso não permitido.",
    404: "Recurso não encontrado.",
    405: "Método não permitido para esta rota.",
    409: "Conflito com o estado atual do recurso.",
    413: "Requisição muito grande.",
    415: "Tipo de conteúdo não suportado. Envie JSON.",
    422: "Dados inválidos.",
    429: "Muitas requisições. Tente novamente em instantes.",
}


class APIError(Exception):
    """Erro de negócio/validação com status HTTP e mensagem para o usuário."""

    def __init__(self, status: int, mensagem: str, campos: dict[str, list[str]] | None = None):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem
        self.campos = campos

    def para_dict(self) -> dict:
        corpo = {"erro": self.mensagem}
        if self.campos:
            corpo["campos"] = self.campos
        return corpo


def init_app(app):
    @app.errorhandler(APIError)
    def _api_error(erro: APIError):
        if erro.status >= 500:
            logger.error("Erro de API %s: %s", erro.status, erro.mensagem)
        return jsonify(erro.para_dict()), erro.status

    @app.errorhandler(HTTPException)
    def _http_error(erro: HTTPException):
        # Descrição padrão do Werkzeug (em inglês) vira mensagem em português;
        # descrições passadas em abort(..., description=...) são mantidas.
        padrao = erro.description == type(erro).description
        mensagem = _MENSAGENS_HTTP.get(erro.code, erro.name) if padrao else erro.description
        return jsonify({"erro": mensagem}), erro.code

    @app.errorhandler(Exception)
    def _erro_inesperado(erro: Exception):
        logger.exception("Erro inesperado: %s", erro)
        return jsonify({"erro": "Erro interno do servidor. Tente novamente mais tarde."}), 500
