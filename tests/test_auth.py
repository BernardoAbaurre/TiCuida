"""Cadastro, login, validação do formulário e autorização por papel."""

import pytest

from ticuida.core.cpf import validar_cpf


@pytest.mark.parametrize(
    "cpf, valido",
    [("12345678909", True), ("52998224725", True), ("12345678900", False), ("11111111111", False)],
)
def test_validar_cpf(cpf, valido):
    assert validar_cpf(cpf) is valido


def test_cadastro_com_sucesso_retorna_token(client, dados_cadastro):
    resposta = client.post("/api/auth/cadastro", json=dados_cadastro)
    assert resposta.status_code == 201
    corpo = resposta.json
    assert corpo["token"]
    assert corpo["usuario"]["papel"] == "paciente"
    paciente = corpo["usuario"]["paciente"]
    assert paciente["telefone"] == "27999991111"  # normalizado só com dígitos
    assert paciente["numero_carteirinha"] is None
    assert paciente["consentimento_em"]


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("cpf", "123.456.789-00"),
        ("email", "email-invalido"),
        ("senha", "semnumero"),
        ("senha", "curta1"),
        ("telefone", "1234"),
        ("data_nascimento", "2015-01-01"),
        ("data_nascimento", "2999-01-01"),
        ("nome", "Ana 123"),
        ("consentimento", False),
        ("convenio_id", 0),
    ],
)
def test_cadastro_rejeita_campo_invalido(client, dados_cadastro, campo, valor):
    resposta = client.post("/api/auth/cadastro", json={**dados_cadastro, campo: valor})
    assert resposta.status_code == 422
    assert campo in resposta.json["campos"]


def test_cadastro_sem_campos_obrigatorios(client):
    resposta = client.post("/api/auth/cadastro", json={})
    assert resposta.status_code == 422
    assert resposta.json["campos"]["nome"] == ["Campo obrigatório."]


def test_cadastro_convenio_inexistente(client, dados_cadastro):
    resposta = client.post("/api/auth/cadastro", json={**dados_cadastro, "convenio_id": 999})
    assert resposta.status_code == 422
    assert "convenio_id" in resposta.json["campos"]


def test_cadastro_email_e_cpf_duplicados(client, dados_cadastro):
    assert client.post("/api/auth/cadastro", json=dados_cadastro).status_code == 201
    resposta = client.post("/api/auth/cadastro", json=dados_cadastro)
    assert resposta.status_code == 409
    assert {"email", "cpf"} <= set(resposta.json["campos"])


def test_login_com_sucesso(client):
    resposta = client.post(
        "/api/auth/login", json={"email": "PACIENTE@ticuida.dev", "senha": "Senha@123"}
    )
    assert resposta.status_code == 200
    assert resposta.json["usuario"]["email"] == "paciente@ticuida.dev"


def test_login_senha_errada(client):
    resposta = client.post(
        "/api/auth/login", json={"email": "paciente@ticuida.dev", "senha": "errada"}
    )
    assert resposta.status_code == 401
    assert resposta.json["erro"] == "E-mail ou senha inválidos."


def test_me_exige_token(client):
    resposta = client.get("/api/auth/me")
    assert resposta.status_code == 401
    assert "erro" in resposta.json


def test_me_com_token_invalido(client):
    resposta = client.get("/api/auth/me", headers={"Authorization": "Bearer abc"})
    assert resposta.status_code == 401


def test_me_operador_mostra_unidade(client, operador_headers):
    resposta = client.get("/api/auth/me", headers=operador_headers)
    assert resposta.json["papel"] == "operador"
    assert resposta.json["unidade"]["nome"] == "Pronto Atendimento Praia da Costa"


def test_perfil_do_paciente_e_edicao(client, paciente_headers):
    assert client.get("/api/pacientes/me", headers=paciente_headers).status_code == 200
    resposta = client.put(
        "/api/pacientes/me", json={"telefone": "27 3333-4444"}, headers=paciente_headers
    )
    assert resposta.status_code == 200
    assert resposta.json["telefone"] == "2733334444"


def test_edicao_de_perfil_vazia_e_invalida(client, paciente_headers):
    assert client.put("/api/pacientes/me", json={}, headers=paciente_headers).status_code == 422
    resposta = client.put("/api/pacientes/me", json={"telefone": "1"}, headers=paciente_headers)
    assert resposta.status_code == 422


def test_operador_nao_acessa_rota_de_paciente(client, operador_headers):
    resposta = client.get("/api/pacientes/me", headers=operador_headers)
    assert resposta.status_code == 403
