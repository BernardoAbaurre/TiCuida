from typing import Literal

from pydantic import BaseModel, Field, model_validator


class LotacaoIn(BaseModel):
    nivel: Literal["baixa", "media", "alta"]


class RecomendacaoQuery(BaseModel):
    """Parâmetros de GET /api/unidades (query string)."""

    convenio_id: int | None = Field(default=None, gt=0)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def _coordenadas_juntas(self):
        if (self.lat is None) != (self.lng is None):
            raise ValueError("Informe latitude e longitude juntas.")
        return self
