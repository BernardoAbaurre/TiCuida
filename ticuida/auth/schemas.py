"""Validação dos formulários de cadastro e login (lado do servidor)."""

import re
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ticuida.core.cpf import validar_cpf
from ticuida.core.tempo import calcular_idade
from ticuida.core.validacao import normalizar_email, normalizar_telefone, somente_digitos

IDADE_MINIMA = 18


class LoginIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=255)
    senha: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def _email(cls, valor: str) -> str:
        return valor.lower()


class CadastroPacienteIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(max_length=255)
    senha: str = Field(min_length=8, max_length=128)
    nome: str = Field(min_length=3, max_length=150)
    cpf: str
    data_nascimento: date
    telefone: str
    contato_emergencia_nome: str = Field(min_length=3, max_length=150)
    contato_emergencia_telefone: str
    convenio_id: int = Field(gt=0)
    numero_carteirinha: str | None = Field(default=None, max_length=30)
    consentimento: bool

    @field_validator("email")
    @classmethod
    def _email(cls, valor: str) -> str:
        return normalizar_email(valor)

    @field_validator("senha")
    @classmethod
    def _senha(cls, valor: str) -> str:
        if not re.search(r"[A-Za-z]", valor) or not re.search(r"\d", valor):
            raise ValueError("A senha deve ter letras e números.")
        return valor

    @field_validator("nome", "contato_emergencia_nome")
    @classmethod
    def _nome(cls, valor: str) -> str:
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' .-]+", valor):
            raise ValueError("Use apenas letras e espaços.")
        return re.sub(r"\s+", " ", valor)

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, valor: str) -> str:
        cpf = somente_digitos(valor)
        if not validar_cpf(cpf):
            raise ValueError("CPF inválido.")
        return cpf

    @field_validator("data_nascimento")
    @classmethod
    def _nascimento(cls, valor: date) -> date:
        if valor > date.today():
            raise ValueError("A data de nascimento não pode ser no futuro.")
        idade = calcular_idade(valor)
        if idade < IDADE_MINIMA:
            raise ValueError("O TiCuida atende apenas maiores de 18 anos.")
        if idade > 120:
            raise ValueError("Data de nascimento inválida.")
        return valor

    @field_validator("telefone", "contato_emergencia_telefone")
    @classmethod
    def _telefone(cls, valor: str) -> str:
        return normalizar_telefone(valor)

    @field_validator("numero_carteirinha")
    @classmethod
    def _carteirinha(cls, valor: str | None) -> str | None:
        return valor or None

    @field_validator("consentimento")
    @classmethod
    def _consentimento(cls, valor: bool) -> bool:
        if not valor:
            raise ValueError("É preciso aceitar o termo de consentimento para usar o TiCuida.")
        return valor
