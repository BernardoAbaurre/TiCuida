"""Validação de entrada no servidor com Pydantic e mensagens em português.

As rotas chamam `validar(Schema, obter_json())`. Se algo estiver errado, a API
responde 422 no formato {"erro": "...", "campos": {"campo": ["mensagem"]}},
que o front-end usa para destacar cada campo do formulário.
"""

import re
from typing import TypeVar

from email_validator import EmailNotValidError, validate_email
from flask import request
from pydantic import BaseModel, ValidationError

from ticuida.errors import APIError

Modelo = TypeVar("Modelo", bound=BaseModel)

_MENSAGENS = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Deve ter pelo menos {min_length} caractere(s).",
    "string_too_long": "Deve ter no máximo {max_length} caracteres.",
    "too_long": "Deve ter no máximo {max_length} item(ns).",
    "greater_than": "Deve ser maior que {gt}.",
    "greater_than_equal": "Deve ser maior ou igual a {ge}.",
    "less_than": "Deve ser menor que {lt}.",
    "less_than_equal": "Deve ser menor ou igual a {le}.",
    "int_parsing": "Deve ser um número inteiro.",
    "int_type": "Deve ser um número inteiro.",
    "int_from_float": "Deve ser um número inteiro.",
    "float_parsing": "Deve ser um número.",
    "float_type": "Deve ser um número.",
    "bool_parsing": "Deve ser verdadeiro ou falso.",
    "bool_type": "Deve ser verdadeiro ou falso.",
    "string_type": "Deve ser um texto.",
    "list_type": "Deve ser uma lista.",
    "date_parsing": "Data inválida (use o formato AAAA-MM-DD).",
    "date_from_datetime_parsing": "Data inválida (use o formato AAAA-MM-DD).",
    "date_type": "Data inválida (use o formato AAAA-MM-DD).",
    "literal_error": "Valor inválido. Opções aceitas: {expected}.",
}


def obter_json() -> dict:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise APIError(400, "Envie os dados em JSON (Content-Type: application/json).")
    return dados


def validar(modelo: type[Modelo], dados: dict) -> Modelo:
    try:
        return modelo.model_validate(dados)
    except ValidationError as exc:
        raise APIError(
            422, "Dados inválidos. Corrija os campos destacados.", campos=traduzir_erros(exc)
        ) from None


def traduzir_erros(exc: ValidationError) -> dict[str, list[str]]:
    campos: dict[str, list[str]] = {}
    for erro in exc.errors(include_url=False):
        # Erros em itens de lista (ex.: sintomas.0) são agrupados no campo da lista
        campo = str(erro["loc"][0]) if erro["loc"] else "_geral"
        mensagem = _mensagem(erro)
        mensagens = campos.setdefault(campo, [])
        if mensagem not in mensagens:
            mensagens.append(mensagem)
    return campos


def _mensagem(erro: dict) -> str:
    tipo = erro["type"]
    contexto = erro.get("ctx") or {}
    if tipo == "value_error":
        return str(contexto.get("error", erro["msg"]))
    modelo = _MENSAGENS.get(tipo)
    if modelo is None:
        return "Valor inválido."
    if "expected" in contexto:
        contexto = {**contexto, "expected": str(contexto["expected"]).replace(" or ", " ou ")}
    try:
        return modelo.format(**contexto)
    except (KeyError, IndexError):
        return modelo


# ---------------------------------------------------------------------------
# Normalizadores reutilizados pelos schemas (lançam ValueError com texto em pt)
# ---------------------------------------------------------------------------
def somente_digitos(valor: str | None) -> str:
    return re.sub(r"\D", "", valor or "")


def normalizar_email(valor: str) -> str:
    try:
        return validate_email(valor, check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        raise ValueError("E-mail inválido.") from None


def normalizar_telefone(valor: str) -> str:
    digitos = somente_digitos(valor)
    if len(digitos) not in (10, 11):
        raise ValueError("Telefone deve ter DDD + número (10 ou 11 dígitos).")
    return digitos
