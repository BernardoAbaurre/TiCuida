from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ticuida.core.cpf import mascarar_cpf
from ticuida.core.tempo import agora, calcular_idade, iso
from ticuida.ext.db import db

if TYPE_CHECKING:
    from ticuida.auth.models import Usuario
    from ticuida.triagem.models import Triagem
    from ticuida.unidades.models import Convenio


class Paciente(db.Model):
    """Perfil 1:1 com um usuário de papel 'paciente'. Guarda só o mínimo (LGPD)."""

    __tablename__ = "pacientes"
    __table_args__ = (CheckConstraint("length(cpf) = 11", name="cpf"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True
    )
    nome: Mapped[str] = mapped_column(String(150))
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    data_nascimento: Mapped[date] = mapped_column(Date)
    telefone: Mapped[str] = mapped_column(String(20))
    contato_emergencia_nome: Mapped[str] = mapped_column(String(150))
    contato_emergencia_telefone: Mapped[str] = mapped_column(String(20))
    convenio_id: Mapped[int] = mapped_column(
        ForeignKey("convenios.id", ondelete="RESTRICT"), index=True
    )
    numero_carteirinha: Mapped[str | None] = mapped_column(String(30))
    consentimento_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora, onupdate=agora
    )

    usuario: Mapped[Usuario] = relationship(back_populates="paciente")
    convenio: Mapped[Convenio] = relationship()
    triagens: Mapped[list[Triagem]] = relationship(
        back_populates="paciente", cascade="all, delete-orphan", order_by="desc(Triagem.criada_em)"
    )

    @property
    def idade(self) -> int:
        return calcular_idade(self.data_nascimento)

    def para_dict(self) -> dict:
        """Visão do próprio paciente (perfil completo)."""
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.isoformat(),
            "idade": self.idade,
            "telefone": self.telefone,
            "contato_emergencia_nome": self.contato_emergencia_nome,
            "contato_emergencia_telefone": self.contato_emergencia_telefone,
            "convenio": self.convenio.para_dict() if self.convenio else None,
            "numero_carteirinha": self.numero_carteirinha,
            "consentimento_em": iso(self.consentimento_em),
        }

    def para_dict_operador(self) -> dict:
        """Visão da unidade: o necessário para o atendimento, com CPF mascarado."""
        return {
            "nome": self.nome,
            "cpf": mascarar_cpf(self.cpf),
            "idade": self.idade,
            "telefone": self.telefone,
            "contato_emergencia_nome": self.contato_emergencia_nome,
            "contato_emergencia_telefone": self.contato_emergencia_telefone,
            "convenio": self.convenio.nome if self.convenio else None,
            "numero_carteirinha": self.numero_carteirinha,
        }
