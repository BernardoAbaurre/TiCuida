"""Fixtures: app com banco SQLite em memória, dados do seed e logins prontos."""

import pytest
from sqlalchemy import select

from ticuida import create_app
from ticuida.config import TestConfig
from ticuida.core.cpf import calcular_digitos
from ticuida.ext.db import db
from ticuida.seed import PACIENTE_DEMO, executar_seed
from ticuida.triagem.models import Sintoma
from ticuida.unidades.models import Convenio, Unidade

SENHA = "Senha@123"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        executar_seed(senha=SENHA)
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def autenticar(client, email: str, senha: str = SENHA) -> dict:
    resposta = client.post("/api/auth/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.json
    return {"Authorization": f"Bearer {resposta.json['token']}"}


def gerar_cpf(base: str) -> str:
    return base + calcular_digitos(base)


@pytest.fixture
def paciente_headers(client):
    return autenticar(client, PACIENTE_DEMO["email"])


@pytest.fixture
def operador_headers(client):
    """Operador da unidade "Pronto Atendimento Praia da Costa"."""
    return autenticar(client, "operador.praiadacosta@ticuida.dev")


@pytest.fixture
def outro_operador_headers(client):
    """Operador de outra unidade (Hospital Costa Azul)."""
    return autenticar(client, "operador.gloria@ticuida.dev")


@pytest.fixture
def convenio_id():
    return db.session.scalar(select(Convenio.id).where(Convenio.nome == "SaúdeMais"))


@pytest.fixture
def unidade(app):
    return db.session.scalar(
        select(Unidade).where(Unidade.nome == "Pronto Atendimento Praia da Costa")
    )


@pytest.fixture
def unidade_outra(app):
    return db.session.scalar(select(Unidade).where(Unidade.nome == "Hospital Costa Azul"))


@pytest.fixture
def sintoma_comum_id(app):
    return db.session.scalar(select(Sintoma.id).where(Sintoma.nome == "Tosse"))


@pytest.fixture
def sintoma_alarme_id(app):
    return db.session.scalar(select(Sintoma.id).where(Sintoma.nome == "Dor forte no peito"))


@pytest.fixture
def dados_cadastro(convenio_id):
    return {
        "email": "novo.paciente@ticuida.dev",
        "senha": "Segura123",
        "nome": "Ana Teste Souza",
        "cpf": gerar_cpf("529982247"),
        "data_nascimento": "1985-03-10",
        "telefone": "(27) 99999-1111",
        "contato_emergencia_nome": "Carlos Souza",
        "contato_emergencia_telefone": "27 98888-2222",
        "convenio_id": convenio_id,
        "numero_carteirinha": "",
        "consentimento": True,
    }


def criar_triagem(client, headers, **extra) -> dict:
    corpo = {
        "queixa_principal": "Dor de garganta há dois dias",
        "sintomas": [],
        "intensidade": 3,
        "inicio_sintomas": "1_a_3_dias",
        **extra,
    }
    resposta = client.post("/api/triagens", json=corpo, headers=headers)
    assert resposta.status_code == 201, resposta.json
    return resposta.json
