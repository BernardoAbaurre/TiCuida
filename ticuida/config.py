"""Configurações da aplicação, lidas de variáveis de ambiente (.env)."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _url_banco() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///ticuida.db")
    # Alguns provedores ainda entregam o esquema antigo "postgres://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-chave-secreta-ticuida-trocar-em-producao")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-chave-jwt-ticuida-trocar-em-producao-0123")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRA_HORAS", "8")))

    # SQLite relativo é criado dentro de instance/ pelo Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = _url_banco()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = [
        origem.strip()
        for origem in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origem.strip()
    ]

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))

    FUSO_HORARIO = os.getenv("FUSO_HORARIO", "America/Sao_Paulo")
    PASSWORD_HASH_METHOD = "scrypt"
    SEED_SENHA = os.getenv("SEED_SENHA", "Ticuida@2026")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "chave-jwt-de-teste-com-mais-de-32-bytes-0123456789"
    LOG_DIR = None
    LOG_LEVEL = "WARNING"
    # Hash mais rápido só nos testes (o seed cria várias contas por teste)
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:1000"
