import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ticuida.core.validacao import normalizar_telefone


class PerfilUpdateIn(BaseModel):
    """Edição parcial do perfil: só os campos enviados são alterados."""

    model_config = ConfigDict(str_strip_whitespace=True)

    telefone: str | None = None
    contato_emergencia_nome: str | None = Field(default=None, min_length=3, max_length=150)
    contato_emergencia_telefone: str | None = None
    convenio_id: int | None = Field(default=None, gt=0)
    numero_carteirinha: str | None = Field(default=None, max_length=30)

    @field_validator("telefone", "contato_emergencia_telefone")
    @classmethod
    def _telefone(cls, valor: str | None) -> str | None:
        return normalizar_telefone(valor) if valor is not None else None

    @field_validator("contato_emergencia_nome")
    @classmethod
    def _nome(cls, valor: str | None) -> str | None:
        if valor is not None and not re.fullmatch(r"[A-Za-zÀ-ÿ' .-]+", valor):
            raise ValueError("Use apenas letras e espaços.")
        return valor

    @model_validator(mode="after")
    def _algum_campo(self):
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        return self
