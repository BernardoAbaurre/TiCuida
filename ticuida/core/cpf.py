"""Validação de CPF pelos dígitos verificadores."""


def calcular_digitos(base: str) -> str:
    """Recebe os 9 primeiros dígitos e devolve os 2 dígitos verificadores."""
    digitos = [int(d) for d in base]
    for tamanho in (9, 10):
        soma = sum(valor * (tamanho + 1 - i) for i, valor in enumerate(digitos[:tamanho]))
        digitos.append((soma * 10 % 11) % 10)
    return f"{digitos[9]}{digitos[10]}"


def validar_cpf(cpf: str) -> bool:
    """CPF com 11 dígitos numéricos, não repetidos e com verificadores corretos."""
    if len(cpf) != 11 or not cpf.isdigit() or cpf == cpf[0] * 11:
        return False
    return cpf[9:] == calcular_digitos(cpf[:9])


def mascarar_cpf(cpf: str) -> str:
    """Exibe só o miolo do CPF (ex.: ***.456.789-**), para telas do operador."""
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**"
