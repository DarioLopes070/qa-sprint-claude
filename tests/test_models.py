import pytest
from qa_sprint.models import Project
from qa_sprint.extensions import db


class TestProjectModel:
    """Testes para o modelo Project."""

    def test_create_project(self, db):
        """Testa criação e persistência de projeto."""
        project = Project(name='Projeto A', description='Descrição', status='Ativo')
        db.session.add(project)
        db.session.commit()

        assert project.id is not None
        assert project.name == 'Projeto A'
        assert project.description == 'Descrição'
        assert project.status == 'Ativo'
        assert project.created_at is not None

    def test_create_project_default_status(self, db):
        """Testa status padrão 'Ativo'."""
        project = Project(name='Projeto B')
        db.session.add(project)
        db.session.commit()

        assert project.status == 'Ativo'

    def test_reject_empty_name(self, db):
        """Testa rejeição de nome vazio."""
        project = Project(name='   ', description='Teste', status='Ativo')
        errors = project.validate()
        assert 'Nome é obrigatório.' in errors

    def test_reject_name_too_long(self, db):
        """Testa rejeição de nome acima de 120 caracteres."""
        long_name = 'A' * 121
        project = Project(name=long_name, status='Ativo')
        errors = project.validate()
        assert 'Nome deve ter no máximo 120 caracteres.' in errors

    def test_reject_invalid_status(self, db):
        """Testa rejeição de status inválido."""
        project = Project(name='Projeto C', status='Invalido')
        errors = project.validate()
        assert any('Status inválido' in e for e in errors)

    def test_strip_name_whitespace(self, db):
        """Testa remoção de espaços nas extremidades do nome."""
        project = Project(name='  Projeto com espaços  ', status='Ativo')
        errors = project.validate()
        assert errors == []
        assert project.name == 'Projeto com espaços'

    def test_valid_statuses(self, db):
        """Testa status válidos."""
        for status in ['Ativo', 'Arquivado']:
            project = Project(name=f'Projeto {status}', status=status)
            errors = project.validate()
            assert errors == []

    def test_get_total_count(self, db):
        """Testa contagem total de projetos."""
        assert Project.get_total_count() == 0
        db.session.add(Project(name='P1', status='Ativo'))
        db.session.add(Project(name='P2', status='Arquivado'))
        db.session.commit()
        assert Project.get_total_count() == 2

    def test_get_active_count(self, db):
        """Testa contagem de projetos ativos."""
        assert Project.get_active_count() == 0
        db.session.add(Project(name='P1', status='Ativo'))
        db.session.add(Project(name='P2', status='Arquivado'))
        db.session.commit()
        assert Project.get_active_count() == 1