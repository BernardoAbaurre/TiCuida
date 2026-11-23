from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TriagemIn(BaseModel):
    """Dados das 4 etapas do formulário de triagem."""

    model_config = ConfigDict(str_strip_whitespace=True)

    queixa_principal: str = Field(min_length=3, max_length=500)
    sintomas: list[int] = Field(default_factory=list, max_length=30)
    intensidade: int = Field(ge=0, le=10)
    inicio_sintomas: Literal["menos_24h", "1_a_3_dias", "mais_3_dias"]
    temperatura: float | None = Field(default=None, ge=34.0, le=43.0)

    @field_validator("sintomas")
    @classmethod
    def _sem_repetidos(cls, valor: list[int]) -> list[int]:
        return sorted(set(valor))

    @field_validator("temperatura")
    @classmethod
    def _uma_casa(cls, valor: float | None) -> float | None:
        return round(valor, 1) if valor is not None else None
