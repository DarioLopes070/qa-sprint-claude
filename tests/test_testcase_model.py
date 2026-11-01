import pytest
from qa_sprint.models import Project, TestCase, TestExecution
from qa_sprint.extensions import db


class TestTestCaseModel:
    """Testes para o modelo TestCase."""

    def test_create_test_case(self, db):
        """Testa criação e persistência de caso de teste."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(
            title='Caso de Teste 1',
            steps='Passo 1\nPasso 2',
            expected_result='Resultado esperado',
            project_id=project.id
        )
        db.session.add(test_case)
        db.session.commit()

        assert test_case.id is not None
        assert test_case.title == 'Caso de Teste 1'
        assert test_case.steps == 'Passo 1\nPasso 2'
        assert test_case.expected_result == 'Resultado esperado'
        assert test_case.project_id == project.id
        assert test_case.created_at is not None

    def test_reject_empty_title(self, db):
        """Testa rejeição de título vazio."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='   ', steps='Passos', expected_result='Resultado', project_id=project.id)
        errors = test_case.validate()
        assert 'Título é obrigatório.' in errors

    def test_reject_title_too_long(self, db):
        """Testa rejeição de título acima de 200 caracteres."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        long_title = 'A' * 201
        test_case = TestCase(title=long_title, steps='Passos', expected_result='Resultado', project_id=project.id)
        errors = test_case.validate()
        assert 'Título deve ter no máximo 200 caracteres.' in errors

    def test_reject_empty_steps(self, db):
        """Testa rejeição de passos vazios."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='Título', steps='   ', expected_result='Resultado', project_id=project.id)
        errors = test_case.validate()
        assert 'Passos de execução são obrigatórios.' in errors

    def test_reject_empty_expected_result(self, db):
        """Testa rejeição de resultado esperado vazio."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='Título', steps='Passos', expected_result='   ', project_id=project.id)
        errors = test_case.validate()
        assert 'Resultado esperado é obrigatório.' in errors

    def test_reject_missing_project(self, db):
        """Testa rejeição de caso de teste sem projeto."""
        test_case = TestCase(title='Título', steps='Passos', expected_result='Resultado', project_id=None)
        errors = test_case.validate()
        assert 'Projeto é obrigatório.' in errors

    def test_strip_whitespace(self, db):
        """Testa remoção de espaços nas extremidades."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(
            title='  Caso com espaços  ',
            steps='  Passos  ',
            expected_result='  Resultado  ',
            project_id=project.id
        )
        errors = test_case.validate()
        assert errors == []
        assert test_case.title == 'Caso com espaços'
        assert test_case.steps == 'Passos'
        assert test_case.expected_result == 'Resultado'

    def test_get_by_project(self, db):
        """Testa busca de casos de teste por projeto."""
        project1 = Project(name='Projeto 1', status='Ativo')
        project2 = Project(name='Projeto 2', status='Ativo')
        db.session.add_all([project1, project2])
        db.session.commit()

        tc1 = TestCase(title='TC1', steps='s', expected_result='r', project_id=project1.id)
        tc2 = TestCase(title='TC2', steps='s', expected_result='r', project_id=project1.id)
        tc3 = TestCase(title='TC3', steps='s', expected_result='r', project_id=project2.id)
        db.session.add_all([tc1, tc2, tc3])
        db.session.commit()

        cases_p1 = TestCase.get_by_project(project1.id)
        cases_p2 = TestCase.get_by_project(project2.id)

        assert len(cases_p1) == 2
        assert len(cases_p2) == 1
        assert cases_p1[0].title == 'TC2'  # Ordenado por created_at desc
        assert cases_p2[0].title == 'TC3'

    def test_get_last_execution_status(self, db):
        """Testa obtenção do último status de execução."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        assert test_case.get_last_execution_status() == 'Não executado'

        exec1 = TestExecution(test_case_id=test_case.id, status='aprovado')
        db.session.add(exec1)
        db.session.commit()

        assert test_case.get_last_execution_status() == 'aprovado'

        exec2 = TestExecution(test_case_id=test_case.id, status='reprovado')
        db.session.add(exec2)
        db.session.commit()

        assert test_case.get_last_execution_status() == 'reprovado'

    def test_get_last_execution(self, db):
        """Testa obtenção da última execução."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        assert test_case.get_last_execution() is None

        exec1 = TestExecution(test_case_id=test_case.id, status='aprovado')
        db.session.add(exec1)
        db.session.commit()

        assert test_case.get_last_execution() is not None
        assert test_case.get_last_execution().status == 'aprovado'

    def test_cascade_delete_executions(self, db):
        """Testa exclusão em cascata das execuções ao excluir caso de teste."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        exec1 = TestExecution(test_case_id=test_case.id, status='aprovado')
        exec2 = TestExecution(test_case_id=test_case.id, status='reprovado')
        db.session.add_all([exec1, exec2])
        db.session.commit()

        assert TestExecution.query.count() == 2

        db.session.delete(test_case)
        db.session.commit()

        assert TestCase.query.count() == 0
        assert TestExecution.query.count() == 0


class TestTestExecutionModel:
    """Testes para o modelo TestExecution."""

    def test_create_execution(self, db):
        """Testa criação e persistência de execução."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        execution = TestExecution(
            test_case_id=test_case.id,
            status='aprovado',
            observations='Teste passou conforme esperado'
        )
        db.session.add(execution)
        db.session.commit()

        assert execution.id is not None
        assert execution.test_case_id == test_case.id
        assert execution.status == 'aprovado'
        assert execution.observations == 'Teste passou conforme esperado'
        assert execution.executed_at is not None

    def test_reject_invalid_status(self, db):
        """Testa rejeição de status inválido."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        execution = TestExecution(test_case_id=test_case.id, status='invalido')
        errors = execution.validate()
        assert any('Status inválido' in e for e in errors)

    def test_valid_statuses(self, db):
        """Testa status válidos."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        test_case = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        db.session.add(test_case)
        db.session.commit()

        for status in ['aprovado', 'reprovado', 'bloqueado']:
            execution = TestExecution(test_case_id=test_case.id, status=status)
            errors = execution.validate()
            assert errors == [], f"Status {status} deveria ser válido"

    def test_reject_missing_test_case(self, db):
        """Testa rejeição de execução sem caso de teste."""
        execution = TestExecution(test_case_id=None, status='aprovado')
        errors = execution.validate()
        assert 'Caso de teste é obrigatório.' in errors

    def test_get_count_by_status(self, db):
        """Testa contagem de execuções por status."""
        project = Project(name='Projeto Teste', status='Ativo')
        db.session.add(project)
        db.session.commit()

        tc1 = TestCase(title='TC1', steps='s', expected_result='r', project_id=project.id)
        tc2 = TestCase(title='TC2', steps='s', expected_result='r', project_id=project.id)
        db.session.add_all([tc1, tc2])
        db.session.commit()

        db.session.add_all([
            TestExecution(test_case_id=tc1.id, status='aprovado'),
            TestExecution(test_case_id=tc1.id, status='reprovado'),
            TestExecution(test_case_id=tc2.id, status='aprovado'),
            TestExecution(test_case_id=tc2.id, status='bloqueado'),
        ])
        db.session.commit()

        assert TestExecution.get_count_by_status('aprovado') == 2
        assert TestExecution.get_count_by_status('reprovado') == 1
        assert TestExecution.get_count_by_status('bloqueado') == 1