from flask import Flask
from qa_sprint.extensions import db, csrf
from qa_sprint.main import main_bp
from qa_sprint.projects import projects_bp
from qa_sprint.commands import init_app as init_commands
from config import config


def create_app(config_name=None):
    if config_name is None:
        import os
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Inicializa extensões
    db.init_app(app)
    csrf.init_app(app)

    # Registra blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)

    # Registra comandos CLI
    init_commands(app)

    # Cria tabelas se não existirem (apenas em desenvolvimento)
    with app.app_context():
        db.create_all()

    return app