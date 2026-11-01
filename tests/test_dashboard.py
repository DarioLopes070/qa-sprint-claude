import pytest
from qa_sprint.models import Project
from qa_sprint.extensions import db


class TestDashboard:
    """Testes para o dashboard."""

    def test_dashboard_empty(self, client):
        """Testa dashboard sem projetos."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Dashboard'.encode('utf-8') in response.data
        assert 'Total de Projetos'.encode('utf-8') in response.data
        # Verifica o valor exato no elemento stat-value
        assert b'<div class="stat-value">0</div>' in response.data

    def test_dashboard_with_projects(self, client, sample_project):
        """Testa dashboard com projetos."""
        # Adiciona mais um projeto arquivado
        archived = Project(name='Projeto Arquivado', status='Arquivado')
        db.session.add(archived)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200
        assert 'Total de Projetos'.encode('utf-8') in response.data
        # Verifica valores exatos nos elementos stat-value
        assert b'<div class="stat-value">2</div>' in response.data  # Total: 2
        assert 'Projetos Ativos'.encode('utf-8') in response.data
        assert b'<div class="stat-value">1</div>' in response.data  # Ativos: 1
        assert 'Projetos Arquivados'.encode('utf-8') in response.data
        # O terceiro card (arquivados) também tem stat-value com 1
        # Como há dois cards com valor 1, verificamos que aparecem pelo menos duas vezes
        assert response.data.count(b'<div class="stat-value">1</div>') >= 2

    def test_dashboard_link_to_create_project(self, client):
        """Testa link para criar projeto no dashboard."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Novo Projeto'.encode('utf-8') in response.data
        assert '/projetos/novo'.encode('utf-8') in response.data