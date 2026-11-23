"""Comandos de linha de comando (`flask <comando>`)."""

import click


def init_app(app):
    @app.cli.command("seed")
    def seed():
        """Carrega unidades, convênios, sintomas e contas de demonstração."""
        from ticuida.seed import executar_seed

        resumo = executar_seed()
        click.echo("Seed concluído:")
        for chave, valor in resumo.items():
            click.echo(f"  {chave}: {valor}")
