"""Regras de prioridade (MVP 5.4): testadas sem Flask nem banco."""

import pytest

from ticuida.triagem.regras import (
    EMERGENCIA,
    NAO_URGENTE,
    POUCO_URGENTE,
    URGENTE,
    DadosTriagem,
    classificar,
)


def dados(**alteracoes) -> DadosTriagem:
    base = {
        "tem_sinal_alarme": False,
        "intensidade": 0,
        "idade": 30,
        "inicio_sintomas": "1_a_3_dias",
        "temperatura": None,
    }
    return DadosTriagem(**{**base, **alteracoes})


@pytest.mark.parametrize(
    "alteracoes, esperado",
    [
        ({"tem_sinal_alarme": True}, EMERGENCIA),
        ({"tem_sinal_alarme": True, "intensidade": 0}, EMERGENCIA),
        ({"intensidade": 7}, URGENTE),
        ({"intensidade": 10}, URGENTE),
        ({"temperatura": 39.1}, URGENTE),
        ({"idade": 60, "inicio_sintomas": "menos_24h"}, URGENTE),
        ({"idade": 75, "inicio_sintomas": "menos_24h", "intensidade": 1}, URGENTE),
        ({"idade": 60, "inicio_sintomas": "mais_3_dias"}, NAO_URGENTE),
        ({"idade": 59, "inicio_sintomas": "menos_24h"}, NAO_URGENTE),
        ({"intensidade": 6}, POUCO_URGENTE),
        ({"intensidade": 4}, POUCO_URGENTE),
        ({"temperatura": 39.0}, POUCO_URGENTE),
        ({"temperatura": 37.8}, POUCO_URGENTE),
        ({"intensidade": 3}, NAO_URGENTE),
        ({"temperatura": 37.5}, NAO_URGENTE),
        ({}, NAO_URGENTE),
    ],
)
def test_classificacao(alteracoes, esperado):
    assert classificar(dados(**alteracoes)).prioridade == esperado


def test_emergencia_tem_orientacao_do_samu():
    resultado = classificar(dados(tem_sinal_alarme=True))
    assert resultado.emergencia
    assert "192" in resultado.orientacao


def test_urgente_lista_todos_os_motivos():
    resultado = classificar(dados(intensidade=8, temperatura=39.5))
    assert resultado.prioridade == URGENTE
    assert len(resultado.motivos) == 2
