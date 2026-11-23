from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ticuida.core.tempo import agora, iso
from ticuida.ext.db import db

if TYPE_CHECKING:
    from ticuida.triagem.models import Triagem
    from ticuida.unidades.models import Unidade

A_CAMINHO = "a_caminho"
CHEGOU = "chegou"
ATENDIDO = "atendido"
NAO_COMPARECEU = "nao_compareceu"
STATUS = (A_CAMINHO, CHEGOU, ATENDIDO, NAO_COMPARECEU)
STATUS_ATIVOS = (A_CAMINHO, CHEGOU)

# Mudanças de status permitidas ao operador
TRANSICOES = {
    A_CAMINHO: {CHEGOU, NAO_COMPARECEU},
    CHEGOU: {ATENDIDO},
    ATENDIDO: set(),
    NAO_COMPARECEU: set(),
}


class Encaminhamento(db.Model):
    """ "Estou indo": liga uma triagem a uma unidade. Cada triagem gera no máximo um."""

    __tablename__ = "encaminhamentos"
    __table_args__ = (
        CheckConstraint(
            "status IN ('a_caminho', 'chegou', 'atendido', 'nao_compareceu')", name="status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    triagem_id: Mapped[int] = mapped_column(
        ForeignKey("triagens.id", ondelete="CASCADE"), unique=True
    )
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id", ondelete="RESTRICT"))
    protocolo: Mapped[str] = mapped_column(String(8), unique=True)
    status: Mapped[str] = mapped_column(String(15), default=A_CAMINHO)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora, onupdate=agora
    )

    triagem: Mapped[Triagem] = relationship(back_populates="encaminhamento")
    unidade: Mapped[Unidade] = relationship(back_populates="encaminhamentos")

    def _base(self) -> dict:
        return {
            "id": self.id,
            "protocolo": self.protocolo,
            "status": self.status,
            "prioridade": self.triagem.prioridade,
            "criado_em": iso(self.criado_em),
            "atualizado_em": iso(self.atualizado_em),
        }

    def para_dict_paciente(self) -> dict:
        unidade = self.unidade
        return {
            **self._base(),
            "triagem_id": self.triagem_id,
            "unidade": {
                "id": unidade.id,
                "nome": unidade.nome,
                "endereco": unidade.endereco,
                "telefone": unidade.telefone,
                "latitude": unidade.latitude,
                "longitude": unidade.longitude,
            },
        }

    def para_dict_operador(self) -> dict:
        return {
            **self._base(),
            "transicoes_permitidas": sorted(TRANSICOES[self.status]),
            "paciente": self.triagem.paciente.para_dict_operador(),
            "triagem": self.triagem.para_dict(),
        }


db.Index(
    "ix_encaminhamentos_fila",
    Encaminhamento.unidade_id,
    Encaminhamento.status,
    Encaminhamento.criado_em,
)
