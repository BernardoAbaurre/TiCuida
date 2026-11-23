"""TiCuida – Application Factory.

`create_app()` monta a aplicação em etapas: configuração, extensões (cada uma
com seu `init_app`), modelos, handlers de erro e os blueprints de cada domínio.
"""

from flask import Flask

from ticuida import auth, core, encaminhamentos, errors, pacientes, triagem, unidades
from ticuida.config import Config
from ticuida.ext import commands, cors, jwt_auth, logs, migrate
from ticuida.ext import db as ext_db

DOMINIOS = (core, auth, pacientes, triagem, unidades, encaminhamentos)


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensões
    logs.init_app(app)
    ext_db.init_app(app)
    ext_db.register_models()
    migrate.init_app(app)
    jwt_auth.init_app(app)
    cors.init_app(app)

    # Erros em JSON e rotas de cada domínio
    errors.init_app(app)
    for dominio in DOMINIOS:
        dominio.init_app(app)

    commands.init_app(app)

    app.logger.info(
        "TiCuida iniciado (banco: %s)", app.config["SQLALCHEMY_DATABASE_URI"].split(":")[0]
    )
    return app
