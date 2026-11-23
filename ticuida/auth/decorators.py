"""Autorização por papel: `@papel_requerido("operador")` exige login e o papel certo."""

from functools import wraps

from flask_jwt_extended import current_user, jwt_required

from ticuida.errors import APIError


def papel_requerido(*papeis: str):
    def decorador(funcao):
        @wraps(funcao)
        @jwt_required()
        def envoltorio(*args, **kwargs):
            if current_user.papel not in papeis:
                raise APIError(403, "Esta ação não está disponível para o seu perfil.")
            return funcao(*args, **kwargs)

        return envoltorio

    return decorador
