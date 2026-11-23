from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ticuida.core.tempo import agora, iso
from ticuida.ext.db import db

if TYPE_CHECKING:
    from ticuida.encaminhamentos.models import Encaminhamento
    from ticuida.pacientes.models import Paciente

# Associação N:N triagem x sintoma marcado
triagem_sintoma = Table(
    "triagem_sintoma",
    db.metadata,
    Column("triagem_id", ForeignKey("triagens.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "sintoma_id", ForeignKey("sintomas.id", ondelete="RESTRICT"), primary_key=True, index=True
    ),
)


class Sintoma(db.Model):
    """Catálogo de sintomas. `sinal_alarme` leva a prioridade Emergência."""

    __tablename__ = "sintomas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(255))
    sinal_alarme: Mapped[bool] = mapped_column(default=False)
    ativo: Mapped[bool] = mapped_column(default=True)

    def para_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "sinal_alarme": self.sinal_alarme,
        }


class Triagem(db.Model):
    __tablename__ = "triagens"
    __table_args__ = (
        CheckConstraint("intensidade BETWEEN 0 AND 10", name="intensidade"),
        CheckConstraint(
            "inicio_sintomas IN ('menos_24h', '1_a_3_dias', 'mais_3_dias')", name="inicio"
        ),
        CheckConstraint(
            "temperatura IS NULL OR temperatura BETWEEN 34.0 AND 43.0", name="temperatura"
        ),
        CheckConstraint(
            "prioridade IN ('emergencia', 'urgente', 'pouco_urgente', 'nao_urgente')",
            name="prioridade",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id", ondelete="CASCADE"))
    queixa_principal: Mapped[str] = mapped_column(String(500))
    intensidade: Mapped[int] = mapped_column(SmallInteger)
    inicio_sintomas: Mapped[str] = mapped_column(String(15))
    temperatura: Mapped[float | None] = mapped_column(Numeric(3, 1, asdecimal=False))
    prioridade: Mapped[str] = mapped_column(String(15))
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    paciente: Mapped[Paciente] = relationship(back_populates="triagens")
    sintomas: Mapped[list[Sintoma]] = relationship(
        secondary=triagem_sintoma, order_by="Sintoma.nome"
    )
    encaminhamento: Mapped[Encaminhamento | None] = relationship(
        back_populates="triagem", cascade="all, delete-orphan"
    )

    def para_dict(self) -> dict:
        return {
            "id": self.id,
            "queixa_principal": self.queixa_principal,
            "sintomas": [s.para_dict() for s in self.sintomas],
            "intensidade": self.intensidade,
            "inicio_sintomas": self.inicio_sintomas,
            "temperatura": self.temperatura,
            "prioridade": self.prioridade,
            "criada_em": iso(self.criada_em),
            "encaminhamento_id": self.encaminhamento.id if self.encaminhamento else None,
        }


db.Index("ix_triagens_paciente_data", Triagem.paciente_id, Triagem.criada_em.desc())
