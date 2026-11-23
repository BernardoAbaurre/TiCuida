"""Banco de dados: instância do Flask-SQLAlchemy e registro dos modelos."""

import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

# Nomes de constraints iguais aos de docs/banco/schema.sql e estáveis nas migrações
CONVENCAO_NOMES = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCAO_NOMES)


db = SQLAlchemy(model_class=Base)


@event.listens_for(Engine, "connect")
def _ativar_chaves_estrangeiras_sqlite(conexao, _registro):
    """SQLite só aplica FOREIGN KEY / ON DELETE com este PRAGMA ligado."""
    if isinstance(conexao, sqlite3.Connection):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_app(app):
    db.init_app(app)


def register_models():
    """Importa os modelos de todos os domínios para registrá-los no metadata."""
    import ticuida.auth.models  # noqa: F401
    import ticuida.encaminhamentos.models  # noqa: F401
    import ticuida.pacientes.models  # noqa: F401
    import ticuida.triagem.models  # noqa: F401
    import ticuida.unidades.models  # noqa: F401
