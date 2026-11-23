"""Recomendação de unidades (convênio, lotação, distância) e atualização de lotação."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from ticuida.unidades.models import Convenio
from ticuida.unidades.services import distancia_km, recomendar_unidades

# 15h em Vila Velha (UTC-3) = 18h UTC: todas as unidades do seed abertas
TARDE = datetime(2026, 11, 23, 18, 0, tzinfo=timezone.utc)
# 23h em Vila Velha = 02h UTC do dia seguinte: só as unidades 24h abertas
NOITE = datetime(2026, 11, 24, 2, 0, tzinfo=timezone.utc)


def test_distancia_haversine():
    # Centro de Vitória -> Centro de Vila Velha, aproximadamente 2,6 km em linha reta
    assert distancia_km(-20.3155, -40.3128, -20.3297, -40.2925) == pytest.approx(2.6, abs=0.3)
    assert distancia_km(-20.0, -40.0, -20.0, -40.0) == 0


def test_recomendacao_filtra_por_convenio(app):
    medsul = app.extensions["sqlalchemy"].session.scalar(
        select(Convenio.id).where(Convenio.nome == "MedSul")
    )
    nomes = {u["nome"] for u in recomendar_unidades(medsul, momento=TARDE)}
    assert "Pronto Atendimento Cobilândia" not in nomes  # não aceita MedSul
    assert "Hospital Costa Azul" in nomes


def test_recomendacao_ordena_por_lotacao_e_distancia(app):
    unidades = recomendar_unidades(None, -20.3365, -40.2840, momento=TARDE)
    ordem = [(u["lotacao"]["nivel"] if u["lotacao"] else None, u["distancia_km"]) for u in unidades]
    pesos = {"baixa": 0, "media": 1, "alta": 2, None: 3}
    assert ordem == sorted(ordem, key=lambda par: (pesos[par[0]], par[1]))
    # Entre as de lotação baixa, a mais próxima vem primeiro
    baixas = [u for u in unidades if u["lotacao"] and u["lotacao"]["nivel"] == "baixa"]
    assert baixas[0]["nome"] == "Clínica Itapuã Saúde"


def test_unidades_fechadas_vao_para_o_fim(app):
    unidades = recomendar_unidades(None, momento=NOITE)
    abertas = [u["aberta_agora"] for u in unidades]
    assert abertas == sorted(abertas, reverse=True)
    assert not next(u for u in unidades if u["nome"] == "Clínica Itapuã Saúde")["aberta_agora"]


def test_rota_usa_convenio_do_paciente(client, paciente_headers, convenio_id):
    resposta = client.get("/api/unidades?lat=-20.33&lng=-40.29", headers=paciente_headers)
    assert resposta.status_code == 200
    assert resposta.json["convenio_id"] == convenio_id
    assert all(u["distancia_km"] is not None for u in resposta.json["unidades"])
    assert all("SaúdeMais" in u["convenios"] for u in resposta.json["unidades"])


def test_rota_valida_coordenadas(client, paciente_headers):
    assert client.get("/api/unidades?lat=-20.3", headers=paciente_headers).status_code == 422
    assert client.get("/api/unidades?lat=abc&lng=1", headers=paciente_headers).status_code == 422
    assert client.get("/api/unidades?lat=100&lng=1", headers=paciente_headers).status_code == 422


def test_detalhe_de_unidade(client, paciente_headers, unidade):
    resposta = client.get(f"/api/unidades/{unidade.id}", headers=paciente_headers)
    assert resposta.status_code == 200
    assert resposta.json["lotacao"]["nivel"] == "alta"
    assert client.get("/api/unidades/9999", headers=paciente_headers).status_code == 404


def test_operador_atualiza_lotacao_da_propria_unidade(client, operador_headers, unidade):
    resposta = client.post(
        f"/api/unidades/{unidade.id}/lotacao", json={"nivel": "baixa"}, headers=operador_headers
    )
    assert resposta.status_code == 201
    assert resposta.json["nivel"] == "baixa"
    assert resposta.json["minutos_desde_atualizacao"] == 0
    detalhe = client.get(f"/api/unidades/{unidade.id}", headers=operador_headers).json
    assert detalhe["lotacao"]["nivel"] == "baixa"


def test_operador_nao_altera_lotacao_de_outra_unidade(client, operador_headers, unidade_outra):
    resposta = client.post(
        f"/api/unidades/{unidade_outra.id}/lotacao",
        json={"nivel": "baixa"},
        headers=operador_headers,
    )
    assert resposta.status_code == 403


def test_lotacao_valida_nivel_e_papel(client, operador_headers, paciente_headers, unidade):
    url = f"/api/unidades/{unidade.id}/lotacao"
    invalido = client.post(url, json={"nivel": "lotado"}, headers=operador_headers)
    assert invalido.status_code == 422
    assert "nivel" in invalido.json["campos"]
    assert client.post(url, json={"nivel": "baixa"}, headers=paciente_headers).status_code == 403
