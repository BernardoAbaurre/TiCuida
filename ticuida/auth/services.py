import logging

from flask_jwt_extended import create_access_token
from sqlalchemy import select

from ticuida.auth.models import PAPEL_PACIENTE, Usuario
from ticuida.auth.schemas import CadastroPacienteIn
from ticuida.core.tempo import agora
from ticuida.errors import APIError
from ticuida.ext.db import db
from ticuida.pacientes.models import Paciente
from ticuida.unidades.models import Convenio

logger = logging.getLogger(__name__)


def gerar_token(usuario: Usuario) -> str:
    return create_access_token(
        identity=str(usuario.id),
        additional_claims={"papel": usuario.papel, "unidade_id": usuario.unidade_id},
    )


def cadastrar_paciente(dados: CadastroPacienteIn) -> Usuario:
    conflitos: dict[str, list[str]] = {}
    if db.session.scalar(select(Usuario.id).where(Usuario.email == dados.email)):
        conflitos["email"] = ["Já existe uma conta com este e-mail."]
    if db.session.scalar(select(Paciente.id).where(Paciente.cpf == dados.cpf)):
        conflitos["cpf"] = ["Já existe uma conta com este CPF."]
    if conflitos:
        raise APIError(409, "Não foi possível concluir o cadastro.", campos=conflitos)

    convenio = db.session.get(Convenio, dados.convenio_id)
    if not convenio or not convenio.ativo:
        raise APIError(422, "Dados inválidos.", campos={"convenio_id": ["Convênio inválido."]})

    usuario = Usuario(email=dados.email, papel=PAPEL_PACIENTE)
    usuario.definir_senha(dados.senha)
    usuario.paciente = Paciente(
        nome=dados.nome,
        cpf=dados.cpf,
        data_nascimento=dados.data_nascimento,
        telefone=dados.telefone,
        contato_emergencia_nome=dados.contato_emergencia_nome,
        contato_emergencia_telefone=dados.contato_emergencia_telefone,
        convenio=convenio,
        numero_carteirinha=dados.numero_carteirinha,
        consentimento_em=agora(),
    )
    db.session.add(usuario)
    db.session.commit()
    logger.info("Paciente cadastrado (usuario_id=%s)", usuario.id)
    return usuario


def autenticar(email: str, senha: str) -> Usuario:
    usuario = db.session.scalar(select(Usuario).where(Usuario.email == email))
    if not usuario or not usuario.verificar_senha(senha) or not usuario.ativo:
        logger.warning("Tentativa de login sem sucesso")
        raise APIError(401, "E-mail ou senha inválidos.")
    logger.info("Login realizado (usuario_id=%s, papel=%s)", usuario.id, usuario.papel)
    return usuario
