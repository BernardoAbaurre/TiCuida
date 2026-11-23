from __future__ import annotations

from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ticuida.core.tempo import agora, iso
from ticuida.ext.db import db

if TYPE_CHECKING:
    from ticuida.auth.models import Usuario
    from ticuida.encaminhamentos.models import Encaminhamento

TIPOS_UNIDADE = ("pronto_atendimento", "clinica", "hospital")
NIVEIS_LOTACAO = ("baixa", "media", "alta")

# Associação N:N unidade x convênio aceito
unidade_convenio = Table(
    "unidade_convenio",
    db.metadata,
    Column("unidade_id", ForeignKey("unidades.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "convenio_id", ForeignKey("convenios.id", ondelete="CASCADE"), primary_key=True, index=True
    ),
)


class Convenio(db.Model):
    """Convênio aceito pelas unidades. Inclui o registro "Particular"."""

    __tablename__ = "convenios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    ativo: Mapped[bool] = mapped_column(default=True)

    unidades: Mapped[list[Unidade]] = relationship(
        secondary=unidade_convenio, back_populates="convenios"
    )

    def para_dict(self) -> dict:
        return {"id": self.id, "nome": self.nome}


class Unidade(db.Model):
    __tablename__ = "unidades"
    __table_args__ = (
        CheckConstraint("tipo IN ('pronto_atendimento', 'clinica', 'hospital')", name="tipo"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="longitude"),
        CheckConstraint(
            "aberto_24h OR (horario_abertura IS NOT NULL AND horario_fechamento IS NOT NULL)",
            name="horario",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    tipo: Mapped[str] = mapped_column(String(20))
    telefone: Mapped[str | None] = mapped_column(String(20))
    logradouro: Mapped[str] = mapped_column(String(150))
    numero: Mapped[str] = mapped_column(String(10))
    bairro: Mapped[str] = mapped_column(String(80))
    cidade: Mapped[str] = mapped_column(String(80))
    uf: Mapped[str] = mapped_column(String(2))
    cep: Mapped[str | None] = mapped_column(String(8))
    latitude: Mapped[float] = mapped_column(Numeric(9, 6, asdecimal=False))
    longitude: Mapped[float] = mapped_column(Numeric(9, 6, asdecimal=False))
    aberto_24h: Mapped[bool] = mapped_column(default=False)
    horario_abertura: Mapped[time | None] = mapped_column(Time)
    horario_fechamento: Mapped[time | None] = mapped_column(Time)
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    convenios: Mapped[list[Convenio]] = relationship(
        secondary=unidade_convenio, back_populates="unidades", order_by="Convenio.nome"
    )
    operadores: Mapped[list[Usuario]] = relationship(back_populates="unidade")
    encaminhamentos: Mapped[list[Encaminhamento]] = relationship(back_populates="unidade")

    @property
    def endereco(self) -> str:
        return f"{self.logradouro}, {self.numero} – {self.bairro}, {self.cidade}/{self.uf}"

    def aberta_em(self, horario: time) -> bool:
        if self.aberto_24h:
            return True
        abertura, fechamento = self.horario_abertura, self.horario_fechamento
        if abertura <= fechamento:
            return abertura <= horario < fechamento
        return horario >= abertura or horario < fechamento  # atravessa a meia-noite

    def aceita_convenio(self, convenio_id: int) -> bool:
        return any(c.id == convenio_id for c in self.convenios)

    def para_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "telefone": self.telefone,
            "endereco": self.endereco,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "aberto_24h": self.aberto_24h,
            "horario_abertura": (
                self.horario_abertura.strftime("%H:%M") if self.horario_abertura else None
            ),
            "horario_fechamento": (
                self.horario_fechamento.strftime("%H:%M") if self.horario_fechamento else None
            ),
            "convenios": [c.nome for c in self.convenios],
        }


class RegistroLotacao(db.Model):
    """Histórico de lotação informado pelo operador; o atual é o mais recente."""

    __tablename__ = "registros_lotacao"
    __table_args__ = (CheckConstraint("nivel IN ('baixa', 'media', 'alta')", name="nivel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id", ondelete="CASCADE"))
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), index=True
    )
    nivel: Mapped[str] = mapped_column(String(5))
    registrado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)

    unidade: Mapped[Unidade] = relationship()
    operador: Mapped[Usuario] = relationship()

    def para_dict(self) -> dict:
        return {
            "id": self.id,
            "unidade_id": self.unidade_id,
            "nivel": self.nivel,
            "registrado_em": iso(self.registrado_em),
        }


db.Index(
    "ix_registros_lotacao_unidade_data",
    RegistroLotacao.unidade_id,
    RegistroLotacao.registrado_em.desc(),
)
