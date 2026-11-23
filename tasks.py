"""Tarefas de desenvolvimento (invoke). Ex.: `invoke install`, `invoke test`."""

from invoke import task


@task
def install(c):
    """Instala o projeto em modo editável com as dependências de dev e teste."""
    c.run('pip install -e ".[dev,test]"', echo=True)


@task
def db(c):
    """Aplica as migrações no banco configurado em DATABASE_URL."""
    c.run("flask db upgrade", echo=True)


@task
def seed(c):
    """Carrega unidades, convênios, sintomas e contas de demonstração."""
    c.run("flask seed", echo=True)


@task
def run(c):
    """Sobe a API em modo debug na porta 5000."""
    c.run("flask run --debug", echo=True, pty=False)


@task
def test(c, cov=False):
    """Roda os testes (use --cov para relatório de cobertura)."""
    c.run("pytest --cov=ticuida --cov-report=term-missing" if cov else "pytest", echo=True)


@task
def lint(c):
    """Verifica estilo com flake8 e black."""
    c.run("flake8 ticuida tests", echo=True)
    c.run("black --check ticuida tests", echo=True)


@task
def fmt(c):
    """Formata o código com black."""
    c.run("black ticuida tests", echo=True)
