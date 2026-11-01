import pytest
from qa_sprint.models import Project
from qa_sprint.extensions import db


class TestProjectsRoutes:
    """Testes para as rotas de projetos."""

    def test_list_projects_empty(self, client):
        """Testa listagem vazia."""
        response = client.get('/projetos/')
        assert response.status_code == 200
        assert 'Nenhum projeto cadastrado'.encode('utf-8') in response.data
        assert 'Criar Projeto'.encode('utf-8') in response.data

    def test_list_projects_with_data(self, client, sample_project):
        """Testa listagem com projetos."""
        response = client.get('/projetos/')
        assert response.status_code == 200
        assert sample_project.name.encode() in response.data
        assert 'Ativo'.encode('utf-8') in response.data

    def test_create_project_get(self, client):
        """Testa GET para criar projeto."""
        response = client.get('/projetos/novo')
        assert response.status_code == 200
        assert 'Novo Projeto'.encode('utf-8') in response.data
        assert 'Nome'.encode('utf-8') in response.data

    def test_create_project_post_success(self, client, app):
        """Testa criação de projeto via POST."""
        response = client.post('/projetos/novo', data={
            'name': 'Novo Projeto',
            'description': 'Descrição do projeto',
            'status': 'Ativo'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Projeto criado com sucesso'.encode('utf-8') in response.data
        assert 'Novo Projeto'.encode('utf-8') in response.data

        # Verifica no banco
        with app.app_context():
            project = Project.query.filter_by(name='Novo Projeto').first()
            assert project is not None
            assert project.description == 'Descrição do projeto'
            assert project.status == 'Ativo'

    def test_create_project_reject_empty_name(self, client):
        """Testa rejeição de nome vazio na criação."""
        response = client.post('/projetos/novo', data={
            'name': '   ',
            'description': 'Teste',
            'status': 'Ativo'
        })
        assert response.status_code == 200
        assert b'Nome' in response.data
        assert 'obrigat'.encode('utf-8') in response.data.lower()

    def test_create_project_reject_name_too_long(self, client):
        """Testa rejeição de nome acima de 120 caracteres."""
        long_name = 'A' * 121
        response = client.post('/projetos/novo', data={
            'name': long_name,
            'description': 'Teste',
            'status': 'Ativo'
        })
        assert response.status_code == 200
        assert '120 caracteres'.encode('utf-8') in response.data

    def test_create_project_reject_invalid_status(self, client):
        """Testa rejeição de status inválido."""
        response = client.post('/projetos/novo', data={
            'name': 'Projeto Teste',
            'description': 'Teste',
            'status': 'Invalido'
        })
        assert response.status_code == 200
        assert 'Status inv'.encode('utf-8') in response.data

    def test_detail_project(self, client, sample_project):
        """Testa visualização de detalhes."""
        response = client.get(f'/projetos/{sample_project.id}')
        assert response.status_code == 200
        assert sample_project.name.encode() in response.data
        assert 'Ativo'.encode('utf-8') in response.data

    def test_detail_nonexistent_project_404(self, client):
        """Testa 404 para projeto inexistente."""
        response = client.get('/projetos/999')
        assert response.status_code == 404

    def test_edit_project_get(self, client, sample_project):
        """Testa GET para editar projeto."""
        response = client.get(f'/projetos/{sample_project.id}/editar')
        assert response.status_code == 200
        assert 'Editar Projeto'.encode('utf-8') in response.data
        assert sample_project.name.encode() in response.data

    def test_edit_project_post_success(self, client, sample_project, app):
        """Testa edição de projeto via POST."""
        response = client.post(f'/projetos/{sample_project.id}/editar', data={
            'name': 'Projeto Atualizado',
            'description': 'Nova descrição',
            'status': 'Arquivado'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Projeto atualizado com sucesso'.encode('utf-8') in response.data
        assert 'Projeto Atualizado'.encode('utf-8') in response.data
        assert 'Arquivado'.encode('utf-8') in response.data

        # Verifica no banco
        with app.app_context():
            updated = Project.query.get(sample_project.id)
            assert updated.name == 'Projeto Atualizado'
            assert updated.description == 'Nova descrição'
            assert updated.status == 'Arquivado'

    def test_edit_nonexistent_project_404(self, client):
        """Testa 404 ao editar projeto inexistente."""
        response = client.get('/projetos/999/editar')
        assert response.status_code == 404

    def test_delete_project_get_confirmation(self, client, sample_project):
        """Testa GET para confirmação de exclusão."""
        response = client.get(f'/projetos/{sample_project.id}/excluir')
        assert response.status_code == 200
        assert 'Confirmar Exclus'.encode('utf-8') in response.data
        assert sample_project.name.encode() in response.data

    def test_delete_project_post_success(self, client, sample_project, app):
        """Testa exclusão de projeto via POST."""
        project_id = sample_project.id
        response = client.post(f'/projetos/{project_id}/excluir', data={
            'confirm': 'Confirmar exclusão'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Projeto excluído com sucesso'.encode('utf-8') in response.data

        # Verifica que foi removido do banco
        with app.app_context():
            deleted = Project.query.get(project_id)
            assert deleted is None

    def test_delete_project_get_does_not_delete(self, client, sample_project, app):
        """Testa que GET não exclui o projeto."""
        project_id = sample_project.id
        response = client.get(f'/projetos/{project_id}/excluir')
        assert response.status_code == 200

        # Projeto ainda deve existir
        with app.app_context():
            project = Project.query.get(project_id)
            assert project is not None

    def test_delete_nonexistent_project_404(self, client):
        """Testa 404 ao excluir projeto inexistente."""
        response = client.get('/projetos/999/excluir')
        assert response.status_code == 404

    def test_delete_cancel_redirects_to_detail(self, client, sample_project):
        """Testa que cancelar exclusão redireciona para detalhes."""
        response = client.post(f'/projetos/{sample_project.id}/excluir', data={
            'cancel': 'Cancelar'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert sample_project.name.encode('utf-8') in response.data

    def test_create_project_strips_whitespace(self, client, app):
        """Testa que espaços nas extremidades são removidos."""
        response = client.post('/projetos/novo', data={
            'name': '  Projeto com espaços  ',
            'description': 'Teste',
            'status': 'Ativo'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Projeto com espaços'.encode('utf-8') in response.data

        with app.app_context():
            project = Project.query.filter_by(name='Projeto com espaços').first()
            assert project is not None

    def test_create_duplicate_name_rejected(self, client, sample_project):
        """Testa rejeição de nome duplicado."""
        response = client.post('/projetos/novo', data={
            'name': sample_project.name,
            'description': 'Outro',
            'status': 'Ativo'
        })
        assert response.status_code == 200
        assert 'Já existe um projeto com este nome'.encode('utf-8') in response.data