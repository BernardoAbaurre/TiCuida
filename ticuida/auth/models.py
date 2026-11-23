from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from flask import current_app
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from ticuida.core.tempo import agora, iso
from ticuida.ext.db import db

if TYPE_CHECKING:
    from ticuida.pacientes.models import Paciente
    from ticuida.unidades.models import Unidade

PAPEL_PACIENTE = "paciente"
PAPEL_OPERADOR = "operador"


class Usuario(db.Model):
    """Conta de acesso. Operador é sempre vinculado a uma unidade; paciente nunca."""

    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("papel IN ('paciente', 'operador')", name="papel"),
        CheckConstraint(
            "(papel = 'operador' AND unidade_id IS NOT NULL) OR "
            "(papel = 'paciente' AND unidade_id IS NULL)",
            name="operador_unidade",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    papel: Mapped[str] = mapped_column(String(10))
    unidade_id: Mapped[int | None] = mapped_column(
        ForeignKey("unidades.id", ondelete="RESTRICT"), index=True
    )
    ativo: Mapped[bool] = mapped_column(default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=agora, onupdate=agora
    )

    unidade: Mapped[Unidade | None] = relationship(back_populates="operadores")
    paciente: Mapped[Paciente | None] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )

    @property
    def eh_paciente(self) -> bool:
        return self.papel == PAPEL_PACIENTE

    @property
    def eh_operador(self) -> bool:
        return self.papel == PAPEL_OPERADOR

    def definir_senha(self, senha: str) -> None:
        metodo = current_app.config.get("PASSWORD_HASH_METHOD", "scrypt")
        self.senha_hash = generate_password_hash(senha, method=metodo)

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    def para_dict(self) -> dict:
        dados = {
            "id": self.id,
            "email": self.email,
            "papel": self.papel,
            "criado_em": iso(self.criado_em),
        }
        if self.eh_operador and self.unidade:
            dados["unidade"] = {"id": self.unidade.id, "nome": self.unidade.nome}
        if self.eh_paciente and self.paciente:
            dados["paciente"] = self.paciente.para_dict()
        return dados

    def __repr__(self) -> str:
        return f"<Usuario {self.id} {self.papel}>"
