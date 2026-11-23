"""Rotas de sintomas e triagem."""

from conftest import criar_triagem, gerar_cpf


def test_lista_sintomas_com_sinais_de_alarme(client):
    resposta = client.get("/api/sintomas")
    assert resposta.status_code == 200
    alarmes = [s for s in resposta.json if s["sinal_alarme"]]
    assert len(alarmes) == 7
    assert len(resposta.json) > len(alarmes)


def test_triagem_nao_urgente(client, paciente_headers, sintoma_comum_id):
    corpo = criar_triagem(client, paciente_headers, sintomas=[sintoma_comum_id])
    assert corpo["prioridade"] == "nao_urgente"
    assert corpo["emergencia"] is False
    assert corpo["triagem"]["sintomas"][0]["nome"] == "Tosse"


def test_triagem_urgente_por_intensidade(client, paciente_headers):
    corpo = criar_triagem(client, paciente_headers, intensidade=8)
    assert corpo["prioridade"] == "urgente"
    assert corpo["motivos"]


def test_triagem_com_sinal_de_alarme_e_emergencia(client, paciente_headers, sintoma_alarme_id):
    corpo = criar_triagem(client, paciente_headers, sintomas=[sintoma_alarme_id])
    assert corpo["prioridade"] == "emergencia"
    assert corpo["emergencia"] is True
    assert "192" in corpo["orientacao"]


def test_triagem_idoso_com_sintomas_recentes_e_urgente(client, dados_cadastro):
    dados = {**dados_cadastro, "data_nascimento": "1950-01-01", "cpf": gerar_cpf("111444777")}
    token = client.post("/api/auth/cadastro", json=dados).json["token"]
    headers = {"Authorization": f"Bearer {token}"}
    corpo = criar_triagem(client, headers, intensidade=1, inicio_sintomas="menos_24h")
    assert corpo["prioridade"] == "urgente"


def test_triagem_validacao_no_servidor(client, paciente_headers):
    resposta = client.post(
        "/api/triagens",
        json={
            "queixa_principal": "",
            "intensidade": 11,
            "inicio_sintomas": "ontem",
            "temperatura": 50,
        },
        headers=paciente_headers,
    )
    assert resposta.status_code == 422
    assert {"queixa_principal", "intensidade", "inicio_sintomas", "temperatura"} <= set(
        resposta.json["campos"]
    )


def test_triagem_com_sintoma_inexistente(client, paciente_headers):
    resposta = client.post(
        "/api/triagens",
        json={
            "queixa_principal": "Dor",
            "sintomas": [9999],
            "intensidade": 2,
            "inicio_sintomas": "menos_24h",
        },
        headers=paciente_headers,
    )
    assert resposta.status_code == 422
    assert "sintomas" in resposta.json["campos"]


def test_operador_nao_registra_triagem(client, operador_headers):
    resposta = client.post("/api/triagens", json={}, headers=operador_headers)
    assert resposta.status_code == 403


def test_triagem_exige_login(client):
    assert client.post("/api/triagens", json={}).status_code == 401


def test_historico_e_detalhe_da_triagem(client, paciente_headers):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    lista = client.get("/api/triagens", headers=paciente_headers).json
    assert [t["id"] for t in lista] == [triagem_id]
    detalhe = client.get(f"/api/triagens/{triagem_id}", headers=paciente_headers)
    assert detalhe.status_code == 200
    assert detalhe.json["orientacao"]


def test_paciente_nao_ve_triagem_de_outro(client, paciente_headers, dados_cadastro):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    token = client.post("/api/auth/cadastro", json=dados_cadastro).json["token"]
    resposta = client.get(
        f"/api/triagens/{triagem_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resposta.status_code == 404
