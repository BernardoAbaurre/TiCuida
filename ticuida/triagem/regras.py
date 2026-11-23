"""Regras de prioridade da pré-triagem (MVP, seção 5.4).

Módulo propositalmente isolado: não depende de Flask nem do banco, para que as
regras possam ser revisadas por profissionais de saúde e testadas sozinhas.
Inspirado no Protocolo de Manchester, de forma simplificada. NÃO é diagnóstico:
a classificação oficial continua sendo feita pela equipe da unidade.
"""

from dataclasses import dataclass, field

EMERGENCIA = "emergencia"
URGENTE = "urgente"
POUCO_URGENTE = "pouco_urgente"
NAO_URGENTE = "nao_urgente"

PRIORIDADES = (EMERGENCIA, URGENTE, POUCO_URGENTE, NAO_URGENTE)
ORDEM_PRIORIDADE = {prioridade: indice for indice, prioridade in enumerate(PRIORIDADES)}

INICIOS_SINTOMAS = ("menos_24h", "1_a_3_dias", "mais_3_dias")

LIMIAR_FEBRE = 37.8  # °C a partir do qual consideramos febre
LIMIAR_FEBRE_ALTA = 39.0  # febre "acima de 39 °C" é urgente
INTENSIDADE_URGENTE = 7  # dor de 7 a 10
INTENSIDADE_POUCO_URGENTE = 4  # dor de 4 a 6
IDADE_IDOSO = 60

ORIENTACOES = {
    EMERGENCIA: (
        "Sinal de alarme identificado. Ligue agora para o SAMU (192) ou vá à emergência "
        "mais próxima. Não aguarde."
    ),
    URGENTE: "Procure atendimento o quanto antes. Sua chegada será destacada na fila da unidade.",
    POUCO_URGENTE: "Procure atendimento hoje em uma das unidades recomendadas.",
    NAO_URGENTE: "Seus sintomas parecem leves. Escolha a unidade mais conveniente para você.",
}


@dataclass(frozen=True)
class DadosTriagem:
    tem_sinal_alarme: bool
    intensidade: int
    idade: int
    inicio_sintomas: str
    temperatura: float | None = None


@dataclass(frozen=True)
class ResultadoTriagem:
    prioridade: str
    motivos: list[str] = field(default_factory=list)

    @property
    def emergencia(self) -> bool:
        return self.prioridade == EMERGENCIA

    @property
    def orientacao(self) -> str:
        return ORIENTACOES[self.prioridade]


def classificar(dados: DadosTriagem) -> ResultadoTriagem:
    """Aplica as regras da mais grave para a menos grave e explica o motivo."""
    if dados.tem_sinal_alarme:
        return ResultadoTriagem(EMERGENCIA, ["Sinal de alarme informado."])

    temperatura = dados.temperatura
    motivos = []
    if dados.intensidade >= INTENSIDADE_URGENTE:
        motivos.append(f"Intensidade {dados.intensidade} de 10.")
    if temperatura is not None and temperatura > LIMIAR_FEBRE_ALTA:
        motivos.append(f"Febre acima de {LIMIAR_FEBRE_ALTA:.0f} °C.")
    if dados.idade >= IDADE_IDOSO and dados.inicio_sintomas == "menos_24h":
        motivos.append(f"{IDADE_IDOSO} anos ou mais com sintomas há menos de 24 h.")
    if motivos:
        return ResultadoTriagem(URGENTE, motivos)

    if dados.intensidade >= INTENSIDADE_POUCO_URGENTE:
        motivos.append(f"Intensidade {dados.intensidade} de 10.")
    if temperatura is not None and temperatura >= LIMIAR_FEBRE:
        motivos.append(f"Febre de até {LIMIAR_FEBRE_ALTA:.0f} °C.")
    if motivos:
        return ResultadoTriagem(POUCO_URGENTE, motivos)

    return ResultadoTriagem(NAO_URGENTE, ["Sintomas leves, sem sinais de alarme."])
