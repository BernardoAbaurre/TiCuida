from typing import Literal

from pydantic import BaseModel, Field


class EncaminhamentoIn(BaseModel):
    triagem_id: int = Field(gt=0)
    unidade_id: int = Field(gt=0)


class StatusIn(BaseModel):
    status: Literal["a_caminho", "chegou", "atendido", "nao_compareceu"]


class FilaQuery(BaseModel):
    """`ativos` = a caminho + chegou (padrão); `todos` = inclui finalizados."""

    status: Literal["ativos", "todos", "a_caminho", "chegou", "atendido", "nao_compareceu"] = (
        "ativos"
    )
