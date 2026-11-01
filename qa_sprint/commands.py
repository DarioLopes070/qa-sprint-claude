import click
from flask.cli import with_appcontext
from qa_sprint.extensions import db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicializa o banco de dados criando as tabelas se não existirem."""
    db.create_all()
    click.echo('Banco de dados inicializado com sucesso.')


def init_app(app):
    app.cli.add_command(init_db_command)