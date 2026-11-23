"""Carga inicial (seed) com dados FICTÍCIOS de demonstração.

O MVP não tem painel administrativo: unidades, convênios, sintomas e contas de
operador entram por aqui. O seed é idempotente: rodar de novo não duplica nada.
"""

import logging
from datetime import date, time, timedelta

from flask import current_app
from sqlalchemy import select

from ticuida.auth.models import PAPEL_OPERADOR, PAPEL_PACIENTE, Usuario
from ticuida.core.tempo import agora
from ticuida.ext.db import db
from ticuida.pacientes.models import Paciente
from ticuida.triagem.models import Sintoma
from ticuida.unidades.models import Convenio, RegistroLotacao, Unidade

logger = logging.getLogger(__name__)

CONVENIOS = ["Particular", "SaúdeMais", "VidaPlena", "CuidarBem", "MedSul"]

SINTOMAS = [
    # (nome, descrição, sinal de alarme)
    ("Febre", "Temperatura acima do normal ou sensação de febre", False),
    ("Tosse", "Tosse seca ou com catarro", False),
    ("Dor de garganta", "Dor ou ardência ao engolir", False),
    ("Dor de cabeça", "Dor de cabeça sem perda de força ou confusão", False),
    ("Dor abdominal", "Dor ou cólica na barriga", False),
    ("Náusea ou vômito", "Enjoo ou vômitos", False),
    ("Diarreia", "Fezes líquidas várias vezes ao dia", False),
    ("Dor no corpo", "Dores musculares ou nas articulações", False),
    ("Coriza ou nariz entupido", "Nariz escorrendo ou congestionado", False),
    ("Tontura", "Sensação de cabeça leve, sem desmaio", False),
    ("Dor ao urinar", "Ardência ou dor ao urinar", False),
    ("Manchas ou coceira na pele", "Alergia, manchas ou coceira", False),
    ("Dor forte no peito", "Dor intensa, aperto ou queimação no peito", True),
    ("Falta de ar intensa", "Dificuldade grande para respirar ou falar", True),
    ("Desmaio", "Perda de consciência, mesmo que rápida", True),
    ("Convulsão", "Crise convulsiva", True),
    ("Sangramento intenso", "Sangramento que não para", True),
    ("Confusão mental", "Desorientação ou fala confusa repentina", True),
    (
        "Fraqueza súbita em um lado do corpo",
        "Perda de força, boca torta ou formigamento de um lado",
        True,
    ),
]

# Unidades fictícias em Vila Velha e Vitória/ES (coordenadas aproximadas)
UNIDADES = [
    {
        "slug": "praiadacosta",
        "nome": "Pronto Atendimento Praia da Costa",
        "tipo": "pronto_atendimento",
        "telefone": "2730000001",
        "logradouro": "Av. Champagnat",
        "numero": "1200",
        "bairro": "Praia da Costa",
        "cidade": "Vila Velha",
        "cep": "29101220",
        "latitude": -20.336500,
        "longitude": -40.284000,
        "aberto_24h": True,
        "convenios": ["Particular", "SaúdeMais", "VidaPlena", "MedSul"],
        "lotacao": ("alta", 8),
    },
    {
        "slug": "itapua",
        "nome": "Clínica Itapuã Saúde",
        "tipo": "clinica",
        "telefone": "2730000002",
        "logradouro": "Rua Itapemirim",
        "numero": "350",
        "bairro": "Itapuã",
        "cidade": "Vila Velha",
        "cep": "29101540",
        "latitude": -20.353000,
        "longitude": -40.292000,
        "aberto_24h": False,
        "horario": (time(7, 0), time(19, 0)),
        "convenios": ["Particular", "SaúdeMais", "CuidarBem"],
        "lotacao": ("baixa", 15),
    },
    {
        "slug": "gloria",
        "nome": "Hospital Costa Azul",
        "tipo": "hospital",
        "telefone": "2730000003",
        "logradouro": "Av. Jerônimo Monteiro",
        "numero": "900",
        "bairro": "Glória",
        "cidade": "Vila Velha",
        "cep": "29122040",
        "latitude": -20.336000,
        "longitude": -40.309000,
        "aberto_24h": True,
        "convenios": ["Particular", "SaúdeMais", "VidaPlena", "CuidarBem", "MedSul"],
        "lotacao": ("media", 30),
    },
    {
        "slug": "cobilandia",
        "nome": "Pronto Atendimento Cobilândia",
        "tipo": "pronto_atendimento",
        "telefone": "2730000004",
        "logradouro": "Av. Carlos Lindenberg",
        "numero": "4500",
        "bairro": "Cobilândia",
        "cidade": "Vila Velha",
        "cep": "29111000",
        "latitude": -20.358000,
        "longitude": -40.343000,
        "aberto_24h": True,
        "convenios": ["Particular", "VidaPlena", "CuidarBem"],
        "lotacao": ("baixa", 5),
    },
    {
        "slug": "centrovv",
        "nome": "Clínica Centro Vila Velha",
        "tipo": "clinica",
        "telefone": "2730000005",
        "logradouro": "Rua Henrique Moscoso",
        "numero": "780",
        "bairro": "Centro",
        "cidade": "Vila Velha",
        "cep": "29100021",
        "latitude": -20.329000,
        "longitude": -40.292000,
        "aberto_24h": False,
        "horario": (time(8, 0), time(18, 0)),
        "convenios": ["Particular", "SaúdeMais", "MedSul"],
        "lotacao": None,
    },
    {
        "slug": "barradojucu",
        "nome": "Pronto Atendimento Barra do Jucu",
        "tipo": "pronto_atendimento",
        "telefone": "2730000006",
        "logradouro": "Rua Vitória Régia",
        "numero": "60",
        "bairro": "Barra do Jucu",
        "cidade": "Vila Velha",
        "cep": "29125000",
        "latitude": -20.413000,
        "longitude": -40.324000,
        "aberto_24h": True,
        "convenios": ["Particular", "SaúdeMais", "VidaPlena", "CuidarBem"],
        "lotacao": ("baixa", 40),
    },
    {
        "slug": "jardimcamburi",
        "nome": "Clínica Jardim Camburi",
        "tipo": "clinica",
        "telefone": "2730000007",
        "logradouro": "Av. Dante Michelini",
        "numero": "2100",
        "bairro": "Jardim Camburi",
        "cidade": "Vitória",
        "cep": "29090400",
        "latitude": -20.260000,
        "longitude": -40.265000,
        "aberto_24h": False,
        "horario": (time(7, 0), time(22, 0)),
        "convenios": ["Particular", "VidaPlena", "MedSul"],
        "lotacao": ("media", 12),
    },
]

PACIENTE_DEMO = {
    "email": "paciente@ticuida.dev",
    "nome": "Maria Demonstração Silva",
    "cpf": "12345678909",
    "data_nascimento": date(1990, 5, 17),
    "telefone": "27999990000",
    "contato_emergencia_nome": "João Silva",
    "contato_emergencia_telefone": "27988880000",
    "convenio": "SaúdeMais",
    "numero_carteirinha": "SM-000123",
}


def email_operador(slug: str) -> str:
    return f"operador.{slug}@ticuida.dev"


def _obter_ou_criar(modelo, filtro: dict, **valores):
    instancia = db.session.scalar(select(modelo).filter_by(**filtro))
    if instancia:
        return instancia, False
    instancia = modelo(**filtro, **valores)
    db.session.add(instancia)
    return instancia, True


def executar_seed(senha: str | None = None) -> dict:
    senha = senha or current_app.config["SEED_SENHA"]
    resumo = {"convenios": 0, "sintomas": 0, "unidades": 0, "operadores": 0, "pacientes": 0}

    convenios = {}
    for nome in CONVENIOS:
        convenios[nome], criado = _obter_ou_criar(Convenio, {"nome": nome})
        resumo["convenios"] += criado

    for nome, descricao, alarme in SINTOMAS:
        _, criado = _obter_ou_criar(
            Sintoma, {"nome": nome}, descricao=descricao, sinal_alarme=alarme
        )
        resumo["sintomas"] += criado

    db.session.flush()

    for dados in UNIDADES:
        abertura, fechamento = dados.get("horario", (None, None))
        unidade, criada = _obter_ou_criar(
            Unidade,
            {"nome": dados["nome"]},
            tipo=dados["tipo"],
            telefone=dados["telefone"],
            logradouro=dados["logradouro"],
            numero=dados["numero"],
            bairro=dados["bairro"],
            cidade=dados["cidade"],
            uf="ES",
            cep=dados["cep"],
            latitude=dados["latitude"],
            longitude=dados["longitude"],
            aberto_24h=dados["aberto_24h"],
            horario_abertura=abertura,
            horario_fechamento=fechamento,
            convenios=[convenios[n] for n in dados["convenios"]],
        )
        resumo["unidades"] += criada

        operador, criado = _obter_ou_criar(
            Usuario, {"email": email_operador(dados["slug"])}, papel=PAPEL_OPERADOR, unidade=unidade
        )
        if criado:
            operador.definir_senha(senha)
            resumo["operadores"] += 1

        if criada and dados["lotacao"]:
            nivel, minutos_atras = dados["lotacao"]
            db.session.add(
                RegistroLotacao(
                    unidade=unidade,
                    operador=operador,
                    nivel=nivel,
                    registrado_em=agora() - timedelta(minutes=minutos_atras),
                )
            )

    if not db.session.scalar(select(Usuario).filter_by(email=PACIENTE_DEMO["email"])):
        usuario = Usuario(email=PACIENTE_DEMO["email"], papel=PAPEL_PACIENTE)
        usuario.definir_senha(senha)
        campos = {k: v for k, v in PACIENTE_DEMO.items() if k not in ("email", "convenio")}
        usuario.paciente = Paciente(
            **campos, convenio=convenios[PACIENTE_DEMO["convenio"]], consentimento_em=agora()
        )
        db.session.add(usuario)
        resumo["pacientes"] += 1

    db.session.commit()
    logger.info("Seed executado: %s", resumo)
    resumo["senha das contas de demonstração"] = senha
    resumo["paciente demo"] = PACIENTE_DEMO["email"]
    resumo["operadores"] = f"{resumo['operadores']} (ex.: {email_operador(UNIDADES[0]['slug'])})"
    return resumo
