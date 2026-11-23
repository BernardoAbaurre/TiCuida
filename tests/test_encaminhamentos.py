"""'Estou indo', protocolo, fila da unidade e mudança de status."""

from conftest import criar_triagem


def estou_indo(client, headers, triagem_id, unidade_id):
    return client.post(
        "/api/encaminhamentos",
        json={"triagem_id": triagem_id, "unidade_id": unidade_id},
        headers=headers,
    )


def test_estou_indo_gera_protocolo(client, paciente_headers, unidade):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    resposta = estou_indo(client, paciente_headers, triagem_id, unidade.id)
    assert resposta.status_code == 201
    assert len(resposta.json["protocolo"]) == 8
    assert resposta.json["status"] == "a_caminho"
    assert resposta.json["unidade"]["id"] == unidade.id


def test_emergencia_nao_pode_ser_encaminhada(client, paciente_headers, unidade, sintoma_alarme_id):
    triagem_id = criar_triagem(client, paciente_headers, sintomas=[sintoma_alarme_id])["triagem"][
        "id"
    ]
    resposta = estou_indo(client, paciente_headers, triagem_id, unidade.id)
    assert resposta.status_code == 422
    assert "192" in resposta.json["erro"]


def test_triagem_so_pode_ser_encaminhada_uma_vez(client, paciente_headers, unidade):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    assert estou_indo(client, paciente_headers, triagem_id, unidade.id).status_code == 201
    assert estou_indo(client, paciente_headers, triagem_id, unidade.id).status_code == 409


def test_unidade_que_nao_aceita_o_convenio(client, paciente_headers, app):
    from sqlalchemy import select

    from ticuida.unidades.models import Unidade

    cobilandia = app.extensions["sqlalchemy"].session.scalar(
        select(Unidade.id).where(Unidade.nome == "Pronto Atendimento Cobilândia")
    )
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    resposta = estou_indo(client, paciente_headers, triagem_id, cobilandia)
    assert resposta.status_code == 422
    assert "unidade_id" in resposta.json["campos"]


def test_validacao_do_encaminhamento(client, paciente_headers):
    resposta = client.post(
        "/api/encaminhamentos", json={"triagem_id": "x"}, headers=paciente_headers
    )
    assert resposta.status_code == 422
    assert {"triagem_id", "unidade_id"} <= set(resposta.json["campos"])


def test_meus_encaminhamentos(client, paciente_headers, unidade):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    protocolo = estou_indo(client, paciente_headers, triagem_id, unidade.id).json["protocolo"]
    lista = client.get("/api/encaminhamentos/meus", headers=paciente_headers).json
    assert [e["protocolo"] for e in lista] == [protocolo]


def test_fila_ordenada_por_prioridade_e_restrita_a_unidade(
    client, paciente_headers, operador_headers, outro_operador_headers, unidade
):
    leve = criar_triagem(client, paciente_headers, intensidade=1)["triagem"]["id"]
    grave = criar_triagem(client, paciente_headers, intensidade=9)["triagem"]["id"]
    estou_indo(client, paciente_headers, leve, unidade.id)
    estou_indo(client, paciente_headers, grave, unidade.id)

    fila = client.get("/api/encaminhamentos/fila", headers=operador_headers)
    assert fila.status_code == 200
    prioridades = [e["prioridade"] for e in fila.json["encaminhamentos"]]
    assert prioridades == ["urgente", "nao_urgente"]
    item = fila.json["encaminhamentos"][0]
    assert item["paciente"]["cpf"].startswith("***")  # CPF mascarado para a unidade
    assert item["triagem"]["intensidade"] == 9

    outra = client.get("/api/encaminhamentos/fila", headers=outro_operador_headers).json
    assert outra["encaminhamentos"] == []


def test_paciente_nao_acessa_fila(client, paciente_headers):
    assert client.get("/api/encaminhamentos/fila", headers=paciente_headers).status_code == 403


def test_fluxo_de_status(client, paciente_headers, operador_headers, unidade):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    enc_id = estou_indo(client, paciente_headers, triagem_id, unidade.id).json["id"]
    url = f"/api/encaminhamentos/{enc_id}"

    resposta = client.patch(url, json={"status": "chegou"}, headers=operador_headers)
    assert resposta.status_code == 200
    assert resposta.json["transicoes_permitidas"] == ["atendido"]

    invalida = client.patch(url, json={"status": "nao_compareceu"}, headers=operador_headers)
    assert invalida.status_code == 409

    assert (
        client.patch(url, json={"status": "atendido"}, headers=operador_headers).status_code == 200
    )

    ativos = client.get("/api/encaminhamentos/fila", headers=operador_headers).json
    assert ativos["encaminhamentos"] == []
    todos = client.get("/api/encaminhamentos/fila?status=todos", headers=operador_headers).json
    assert todos["encaminhamentos"][0]["status"] == "atendido"


def test_status_invalido_e_filtro_invalido(client, paciente_headers, operador_headers, unidade):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    enc_id = estou_indo(client, paciente_headers, triagem_id, unidade.id).json["id"]
    resposta = client.patch(
        f"/api/encaminhamentos/{enc_id}", json={"status": "sumiu"}, headers=operador_headers
    )
    assert resposta.status_code == 422
    filtro = client.get("/api/encaminhamentos/fila?status=xyz", headers=operador_headers)
    assert filtro.status_code == 422


def test_operador_de_outra_unidade_nao_ve_nem_altera(
    client, paciente_headers, outro_operador_headers, unidade
):
    triagem_id = criar_triagem(client, paciente_headers)["triagem"]["id"]
    enc_id = estou_indo(client, paciente_headers, triagem_id, unidade.id).json["id"]
    url = f"/api/encaminhamentos/{enc_id}"
    assert client.get(url, headers=outro_operador_headers).status_code == 404
    resposta = client.patch(url, json={"status": "chegou"}, headers=outro_operador_headers)
    assert resposta.status_code == 404
