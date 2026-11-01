import pytest
import tempfile
import os
from qa_sprint import create_app
from qa_sprint.extensions import db as _db
from qa_sprint.models import Project


@pytest.fixture(scope='session')
def app():
    """Cria aplicação para testes."""
    app = create_app('testing')
    yield app


@pytest.fixture(scope='function')
def client(app):
    """Cliente de teste com banco fresco para cada teste."""
    with app.app_context():
        _db.create_all()
    yield app.test_client()
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Banco de dados para cada teste - recria tabelas."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def sample_project(db):
    """Cria um projeto de exemplo."""
    project = Project(name='Projeto Teste', description='Descrição do projeto', status='Ativo')
    db.session.add(project)
    db.session.commit()
    return project