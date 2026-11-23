"""Funções de data e hora. Tudo é gravado em UTC; o SQLite devolve datas sem fuso."""

from datetime import date, datetime, timezone


def agora() -> datetime:
    return datetime.now(timezone.utc)


def como_utc(momento: datetime | None) -> datetime | None:
    if momento is None:
        return None
    if momento.tzinfo is None:
        return momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(timezone.utc)


def iso(momento: datetime | None) -> str | None:
    momento = como_utc(momento)
    return momento.isoformat() if momento else None


def minutos_desde(momento: datetime, referencia: datetime | None = None) -> int:
    referencia = como_utc(referencia) if referencia else agora()
    return max(0, int((referencia - como_utc(momento)).total_seconds() // 60))


def calcular_idade(nascimento: date, referencia: date | None = None) -> int:
    referencia = referencia or date.today()
    idade = referencia.year - nascimento.year
    if (referencia.month, referencia.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade
