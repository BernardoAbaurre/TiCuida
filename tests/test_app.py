"""Application Factory, blueprints, health check e erros em JSON."""

from ticuida import create_app
from ticuida.config import TestConfig


def test_factory_cria_apps_independentes():
    app1, app2 = create_app(TestConfig), create_app(TestConfig)
    assert app1 is not app2
    assert app1.config["TESTING"] is True


def test_blueprints_de_todos_os_dominios_registrados(app):
    esperados = {"core", "auth", "pacientes", "triagem", "unidades", "convenios", "encaminhamentos"}
    assert esperados <= set(app.blueprints)


def test_health(client):
    resposta = client.get("/api/health")
    assert resposta.status_code == 200
    assert resposta.json["status"] == "ok"
    assert resposta.json["banco"] == "ok"


def test_rota_inexistente_retorna_json_em_portugues(client):
    resposta = client.get("/api/nao-existe")
    assert resposta.status_code == 404
    assert resposta.json == {"erro": "Recurso não encontrado."}


def test_metodo_nao_permitido(client):
    resposta = client.delete("/api/health")
    assert resposta.status_code == 405
    assert "erro" in resposta.json


def test_corpo_sem_json_retorna_400(client):
    resposta = client.post("/api/auth/login", data="texto", content_type="text/plain")
    assert resposta.status_code == 400
    assert "JSON" in resposta.json["erro"]


def test_convenios_publicos(client):
    resposta = client.get("/api/convenios")
    assert resposta.status_code == 200
    assert "Particular" in [c["nome"] for c in resposta.json]
