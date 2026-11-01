import pytest
from qa_sprint.models import Project, Bug, TestCase
from qa_sprint.extensions import db


class TestBugModel:
    """Testes para o modelo Bug."""

    def test_create_bug(self, db):
        """Testa criação e persistência de bug."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(
            title='Bug 1',
            description='Descrição do bug',
            project_id=project.id,
            severity='alta',
            status='aberto'
        )
        db.session.add(bug)
        db.session.commit()

        assert bug.id is not None
        assert bug.title == 'Bug 1'
        assert bug.description == 'Descrição do bug'
        assert bug.project_id == project.id
        assert bug.severity == 'alta'
        assert bug.status == 'aberto'
        assert bug.created_at is not None

    def test_create_bug_default_status(self, db):
        """Testa status padrão 'aberto'."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(
            title='Bug 1',
            description='Descrição',
            project_id=project.id,
            severity='média'
        )
        db.session.add(bug)
        db.session.commit()

        assert bug.status == 'aberto'

    def test_reject_empty_title(self, db):
        """Testa rejeição de título vazio."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(title='   ', description='Desc', project_id=project.id, severity='baixa', status='aberto')
        errors = bug.validate()
        assert 'Título é obrigatório.' in errors

    def test_reject_title_too_long(self, db):
        """Testa rejeição de título acima de 200 caracteres."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        long_title = 'A' * 201
        bug = Bug(title=long_title, description='Desc', project_id=project.id, severity='baixa', status='aberto')
        errors = bug.validate()
        assert 'Título deve ter no máximo 200 caracteres.' in errors

    def test_reject_empty_description(self, db):
        """Testa rejeição de descrição vazia."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(title='Título', description='   ', project_id=project.id, severity='baixa', status='aberto')
        errors = bug.validate()
        assert 'Descrição é obrigatória.' in errors

    def test_reject_missing_project(self, db):
        """Testa rejeição de bug sem projeto."""
        bug = Bug(title='Título', description='Desc', project_id=None, severity='baixa', status='aberto')
        errors = bug.validate()
        assert 'Projeto é obrigatório.' in errors

    def test_reject_invalid_severity(self, db):
        """Testa rejeição de severidade inválida."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(title='Título', description='Desc', project_id=project.id, severity='invalida', status='aberto')
        errors = bug.validate()
        assert any('Severidade inválida' in e for e in errors)

    def test_reject_invalid_status(self, db):
        """Testa rejeição de status inválido."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(title='Título', description='Desc', project_id=project.id, severity='baixa', status='invalido')
        errors = bug.validate()
        assert any('Status inválido' in e for e in errors)

    def test_valid_severities(self, db):
        """Testa severidades válidas."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        for severity in ['baixa', 'média', 'alta', 'crítica']:
            bug = Bug(title=f'Bug {severity}', description='Desc', project_id=project.id, severity=severity, status='aberto')
            errors = bug.validate()
            assert errors == [], f"Severidade {severity} deveria ser válida"

    def test_valid_statuses(self, db):
        """Testa status válidos."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        for status in ['aberto', 'em andamento', 'resolvido']:
            bug = Bug(title=f'Bug {status}', description='Desc', project_id=project.id, severity='baixa', status=status)
            errors = bug.validate()
            assert errors == [], f"Status {status} deveria ser válido"

    def test_strip_whitespace(self, db):
        """Testa remoção de espaços nas extremidades."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(
            title='  Bug com espaços  ',
            description='  Descrição com espaços  ',
            project_id=project.id,
            severity='baixa',
            status='aberto'
        )
        errors = bug.validate()
        assert errors == []
        assert bug.title == 'Bug com espaços'
        assert bug.description == 'Descrição com espaços'

    def test_get_by_project(self, db):
        """Testa busca de bugs por projeto."""
        project1 = Project(name='Projeto 1', status='Ativo')
        project2 = Project(name='Projeto 2', status='Ativo')
        db.session.add_all([project1, project2])
        db.session.commit()

        bug1 = Bug(title='B1', description='d', project_id=project1.id, severity='baixa', status='aberto')
        bug2 = Bug(title='B2', description='d', project_id=project1.id, severity='alta', status='aberto')
        bug3 = Bug(title='B3', description='d', project_id=project2.id, severity='média', status='aberto')
        db.session.add_all([bug1, bug2, bug3])
        db.session.commit()

        bugs_p1 = Bug.get_by_project(project1.id)
        bugs_p2 = Bug.get_by_project(project2.id)

        assert len(bugs_p1) == 2
        assert len(bugs_p2) == 1
        assert bugs_p1[0].title == 'B2'  # Ordenado por created_at desc
        assert bugs_p2[0].title == 'B3'

    def test_get_count_by_status(self, db):
        """Testa contagem de bugs por status."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        db.session.add_all([
            Bug(title='B1', description='d', project_id=project.id, severity='baixa', status='aberto'),
            Bug(title='B2', description='d', project_id=project.id, severity='alta', status='aberto'),
            Bug(title='B3', description='d', project_id=project.id, severity='média', status='em andamento'),
            Bug(title='B4', description='d', project_id=project.id, severity='crítica', status='resolvido'),
        ])
        db.session.commit()

        assert Bug.get_count_by_status('aberto') == 2
        assert Bug.get_count_by_status('em andamento') == 1
        assert Bug.get_count_by_status('resolvido') == 1

    def test_get_count_by_severity(self, db):
        """Testa contagem de bugs por severidade."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        db.session.add_all([
            Bug(title='B1', description='d', project_id=project.id, severity='baixa', status='aberto'),
            Bug(title='B2', description='d', project_id=project.id, severity='baixa', status='aberto'),
            Bug(title='B3', description='d', project_id=project.id, severity='alta', status='aberto'),
            Bug(title='B4', description='d', project_id=project.id, severity='crítica', status='aberto'),
        ])
        db.session.commit()

        assert Bug.get_count_by_severity('baixa') == 2
        assert Bug.get_count_by_severity('média') == 0
        assert Bug.get_count_by_severity('alta') == 1
        assert Bug.get_count_by_severity('crítica') == 1

    def test_cascade_delete_bugs(self, db):
        """Testa exclusão em cascata de bugs ao excluir projeto."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug1 = Bug(title='B1', description='d', project_id=project.id, severity='baixa', status='aberto')
        bug2 = Bug(title='B2', description='d', project_id=project.id, severity='alta', status='aberto')
        db.session.add_all([bug1, bug2])
        db.session.commit()

        assert Bug.query.count() == 2

        db.session.delete(project)
        db.session.commit()

        assert Project.query.count() == 0
        assert Bug.query.count() == 0


class TestProjectRelationships:
    """Testes para relacionamentos do Project."""

    def test_project_has_test_cases_relationship(self, db):
        """Testa relacionamento Project -> TestCases."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        tc1 = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        tc2 = TestCase(title='TC2', steps='s', expected_result='r', project_id=project.id)
        db.session.add_all([tc1, tc2])
        db.session.commit()

        # Refresh project to get updated relationships
        db.session.refresh(project)
        assert len(project.test_cases) == 2
        # Check both exist (order may vary)
        test_case_titles = [tc.title for tc in project.test_cases]
        assert 'TC1' in test_case_titles
        assert 'TC2' in test_case_titles

    def test_project_has_bugs_relationship(self, db):
        """Testa relacionamento Project -> Bugs."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug1 = Bug(title='B1', description='d', project_id=project.id, severity='baixa', status='aberto')
        bug2 = Bug(title='B2', description='d', project_id=project.id, severity='alta', status='aberto')
        db.session.add_all([bug1, bug2])
        db.session.commit()

        # Refresh project to get updated relationships
        db.session.refresh(project)
        assert len(project.bugs) == 2
        # Order may vary, just check both exist
        bug_titles = [b.title for b in project.bugs]
        assert 'B1' in bug_titles
        assert 'B2' in bug_titles

    def test_cascade_delete_project_removes_test_cases(self, db):
        """Testa exclusão em cascata de test cases ao excluir projeto."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        assert TestCase.query.count() == 1

        db.session.delete(project)
        db.session.commit()

        assert Project.query.count() == 0
        assert TestCase.query.count() == 0

    def test_cascade_delete_project_removes_bugs(self, db):
        """Testa exclusão em cascata de bugs ao excluir projeto."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        bug = Bug(title='B1', description='d', project_id=project.id, severity='baixa', status='aberto')
        db.session.add(bug)
        db.session.commit()

        assert Bug.query.count() == 1

        db.session.delete(project)
        db.session.commit()

        assert Project.query.count() == 0
        assert Bug.query.count() == 0