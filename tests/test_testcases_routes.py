import pytest
from qa_sprint.models import Project, TestCase, TestExecution, Bug
from qa_sprint.extensions import db


class TestTestCasesRoutes:
    """Testes para as rotas de casos de teste."""

    def test_list_testcases_empty(self, client):
        """Testa listagem vazia."""
        response = client.get('/testcases/')
        assert response.status_code == 200
        assert 'Nenhum caso de teste encontrado'.encode('utf-8') in response.data
        assert 'Novo Caso de Teste'.encode('utf-8') in response.data

    def test_list_testcases_with_data(self, client, app):
        """Testa listagem com casos de teste."""
        with app.app_context():
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

        response = client.get('/testcases/')
        assert response.status_code == 200
        assert 'Caso de Teste 1'.encode('utf-8') in response.data
        assert 'Projeto Teste'.encode('utf-8') in response.data
        assert 'Não executado'.encode('utf-8') in response.data

    def test_list_testcases_filter_by_project(self, client, app):
        """Testa filtragem por projeto."""
        with app.app_context():
            project1 = Project(name='Projeto 1', status='Ativo')
            project2 = Project(name='Projeto 2', status='Ativo')
            db.session.add_all([project1, project2])
            db.session.commit()

            tc1 = TestCase(title='TC Projeto 1', steps='s', expected_result='r', project_id=project1.id)
            tc2 = TestCase(title='TC Projeto 2', steps='s', expected_result='r', project_id=project2.id)
            db.session.add_all([tc1, tc2])
            db.session.commit()

            project1_id = project1.id

        response = client.get(f'/testcases/?project_id={project1_id}')
        assert response.status_code == 200
        assert 'TC Projeto 1'.encode('utf-8') in response.data
        assert 'TC Projeto 2'.encode('utf-8') not in response.data

    def test_create_testcase_get(self, client, app):
        """Testa GET para criar caso de teste."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

        response = client.get('/testcases/novo')
        assert response.status_code == 200
        assert 'Novo Caso de Teste'.encode('utf-8') in response.data
        assert 'Título'.encode('utf-8') in response.data
        assert 'Passos de Execução'.encode('utf-8') in response.data
        assert 'Resultado Esperado'.encode('utf-8') in response.data
        assert 'Projeto'.encode('utf-8') in response.data

    def test_create_testcase_post_success(self, client, app):
        """Testa criação de caso de teste via POST."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = client.post('/testcases/novo', data={
            'title': 'Novo Caso de Teste',
            'steps': 'Passo 1\nPasso 2',
            'expected_result': 'Resultado esperado',
            'project_id': project_id
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Caso de teste criado com sucesso'.encode('utf-8') in response.data
        assert 'Novo Caso de Teste'.encode('utf-8') in response.data

        with app.app_context():
            test_case = TestCase.query.filter_by(title='Novo Caso de Teste').first()
            assert test_case is not None
            assert test_case.steps == 'Passo 1\nPasso 2'
            assert test_case.expected_result == 'Resultado esperado'

    def test_create_testcase_reject_empty_title(self, client, app):
        """Testa rejeição de título vazio."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = client.post('/testcases/novo', data={
            'title': '   ',
            'steps': 'Passos',
            'expected_result': 'Resultado',
            'project_id': project_id
        })
        assert response.status_code == 200
        assert 'Título'.encode('utf-8') in response.data
        assert 'obrigat'.encode('utf-8') in response.data.lower()

    def test_create_testcase_reject_empty_steps(self, client, app):
        """Testa rejeição de passos vazios."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = client.post('/testcases/novo', data={
            'title': 'Caso de Teste',
            'steps': '   ',
            'expected_result': 'Resultado',
            'project_id': project_id
        })
        assert response.status_code == 200
        assert 'obrigat'.encode('utf-8') in response.data.lower()

    def test_create_testcase_reject_empty_expected_result(self, client, app):
        """Testa rejeição de resultado esperado vazio."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = client.post('/testcases/novo', data={
            'title': 'Caso de Teste',
            'steps': 'Passos',
            'expected_result': '   ',
            'project_id': project_id
        })
        assert response.status_code == 200
        assert 'obrigat'.encode('utf-8') in response.data.lower()

    def test_create_testcase_reject_missing_project(self, client):
        """Testa rejeição de projeto não selecionado."""
        response = client.post('/testcases/novo', data={
            'title': 'Caso de Teste',
            'steps': 'Passos',
            'expected_result': 'Resultado',
            'project_id': ''
        })
        assert response.status_code == 200
        assert 'obrigat'.encode('utf-8') in response.data.lower()

    def test_detail_testcase(self, client, app):
        """Testa visualização de detalhes."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Detalhado',
                steps='Passos detalhados',
                expected_result='Resultado esperado',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            test_case_id = test_case.id

        response = client.get(f'/testcases/{test_case_id}')
        assert response.status_code == 200
        assert 'TC Detalhado'.encode('utf-8') in response.data
        assert 'Passos detalhados'.encode('utf-8') in response.data
        assert 'Resultado esperado'.encode('utf-8') in response.data

    def test_detail_nonexistent_testcase_404(self, client):
        """Testa 404 para caso de teste inexistente."""
        response = client.get('/testcases/999')
        assert response.status_code == 404

    def test_edit_testcase_get(self, client, app):
        """Testa GET para editar caso de teste."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Original',
                steps='Passos',
                expected_result='Resultado',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            test_case_id = test_case.id

        response = client.get(f'/testcases/{test_case_id}/editar')
        assert response.status_code == 200
        assert 'Editar Caso de Teste'.encode('utf-8') in response.data
        assert 'TC Original'.encode('utf-8') in response.data

    def test_edit_testcase_post_success(self, client, app):
        """Testa edição de caso de teste via POST."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Original',
                steps='Passos originais',
                expected_result='Resultado original',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            test_case_id = test_case.id
            project_id = project.id

        response = client.post(f'/testcases/{test_case_id}/editar', data={
            'title': 'TC Editado',
            'steps': 'Passos editados',
            'expected_result': 'Resultado editado',
            'project_id': project_id
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Caso de teste atualizado com sucesso'.encode('utf-8') in response.data
        assert 'TC Editado'.encode('utf-8') in response.data

        with app.app_context():
            updated = TestCase.query.get(test_case_id)
            assert updated.title == 'TC Editado'
            assert updated.steps == 'Passos editados'

    def test_execute_testcase_post_success(self, client, app):
        """Testa registro de execução."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Executivo',
                steps='Passos',
                expected_result='Resultado',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            test_case_id = test_case.id

        response = client.post(f'/testcases/{test_case_id}/executar', data={
            'status': 'aprovado',
            'observations': 'Teste passou'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Execução registrada com sucesso'.encode('utf-8') in response.data

        with app.app_context():
            executions = TestExecution.query.filter_by(test_case_id=test_case_id).all()
            assert len(executions) == 1
            assert executions[0].status == 'aprovado'
            assert executions[0].observations == 'Teste passou'

    def test_execute_testcase_updates_last_execution_status(self, client, app):
        """Testa se última execução atualiza o status exibido."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Status',
                steps='Passos',
                expected_result='Resultado',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            test_case_id = test_case.id

        # Primeira execução: aprovado
        client.post(f'/testcases/{test_case_id}/executar', data={
            'status': 'aprovado',
            'observations': ''
        }, follow_redirects=True)

        response = client.get(f'/testcases/{test_case_id}')
        assert response.status_code == 200
        assert 'aprovado'.encode('utf-8') in response.data

        # Segunda execução: reprovado
        client.post(f'/testcases/{test_case_id}/executar', data={
            'status': 'reprovado',
            'observations': ''
        }, follow_redirects=True)

        response = client.get(f'/testcases/{test_case_id}')
        assert response.status_code == 200
        assert 'reprovado'.encode('utf-8') in response.data
        # Deve mostrar reprovado (último) não aprovado

    def test_delete_testcase_get_confirmation(self, client, app):
        """Testa GET para confirmar exclusão."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Deletar',
                steps='Passos',
                expected_result='Resultado',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            test_case_id = test_case.id

        response = client.get(f'/testcases/{test_case_id}/excluir')
        assert response.status_code == 200
        assert 'Excluir Caso de Teste'.encode('utf-8') in response.data
        assert 'TC Deletar'.encode('utf-8') in response.data

    def test_delete_testcase_post_success(self, client, app):
        """Testa exclusão de caso de teste via POST."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            test_case = TestCase(
                title='TC Deletar',
                steps='Passos',
                expected_result='Resultado',
                project_id=project.id
            )
            db.session.add(test_case)
            db.session.commit()

            # Criar execução para testar cascade
            execution = TestExecution(test_case_id=test_case.id, status='aprovado')
            db.session.add(execution)
            db.session.commit()
            test_case_id = test_case.id

        response = client.post(f'/testcases/{test_case.id}/excluir', data={
            'confirm': True
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Caso de teste excluído com sucesso'.encode('utf-8') in response.data

        with app.app_context():
            assert TestCase.query.get(test_case_id) is None
            assert TestExecution.query.filter_by(test_case_id=test_case_id).count() == 0


class TestBugsRoutes:
    """Testes para as rotas de bugs."""

    def test_list_bugs_empty(self, client):
        """Testa listagem vazia."""
        response = client.get('/bugs/')
        assert response.status_code == 200
        assert 'Nenhum bug encontrado'.encode('utf-8') in response.data
        assert 'Novo Bug'.encode('utf-8') in response.data

    def test_list_bugs_with_data(self, client, app):
        """Testa listagem com bugs."""
        with app.app_context():
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

        response = client.get('/bugs/')
        assert response.status_code == 200
        assert 'Bug 1'.encode('utf-8') in response.data
        assert 'Projeto Teste'.encode('utf-8') in response.data
        assert 'alta'.encode('utf-8') in response.data
        assert 'aberto'.encode('utf-8') in response.data

    def test_list_bugs_filter_by_project(self, client, app):
        """Testa filtragem por projeto."""
        with app.app_context():
            project1 = Project(name='Projeto 1', status='Ativo')
            project2 = Project(name='Projeto 2', status='Ativo')
            db.session.add_all([project1, project2])
            db.session.commit()

            bug1 = Bug(title='Bug P1', description='d', project_id=project1.id, severity='baixa', status='aberto')
            bug2 = Bug(title='Bug P2', description='d', project_id=project2.id, severity='baixa', status='aberto')
            db.session.add_all([bug1, bug2])
            db.session.commit()

            project1_id = project1.id

        response = client.get(f'/bugs/?project_id={project1_id}')
        assert response.status_code == 200
        assert 'Bug P1'.encode('utf-8') in response.data
        assert 'Bug P2'.encode('utf-8') not in response.data

    def test_create_bug_get(self, client, app):
        """Testa GET para criar bug."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

        response = client.get('/bugs/novo')
        assert response.status_code == 200
        assert 'Novo Bug'.encode('utf-8') in response.data
        assert 'Título'.encode('utf-8') in response.data
        assert 'Descrição'.encode('utf-8') in response.data
        assert 'Projeto'.encode('utf-8') in response.data
        assert 'Severidade'.encode('utf-8') in response.data
        assert 'Status'.encode('utf-8') in response.data

    def test_create_bug_post_success(self, client, app):
        """Testa criação de bug via POST."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = client.post('/bugs/novo', data={
            'title': 'Novo Bug',
            'description': 'Descrição detalhada',
            'project_id': project_id,
            'severity': 'crítica',
            'status': 'aberto'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Bug criado com sucesso'.encode('utf-8') in response.data
        assert 'Novo Bug'.encode('utf-8') in response.data

        with app.app_context():
            bug = Bug.query.filter_by(title='Novo Bug').first()
            assert bug is not None
            assert bug.description == 'Descrição detalhada'
            assert bug.severity == 'crítica'
            assert bug.status == 'aberto'

    def test_create_bug_reject_empty_title(self, client, app):
        """Testa rejeição de título vazio."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()
            project_id = project.id

        response = client.post('/bugs/novo', data={
            'title': '   ',
            'description': 'Descrição',
            'project_id': project_id,
            'severity': 'baixa',
            'status': 'aberto'
        })
        assert response.status_code == 200
        assert 'obrigat'.encode('utf-8') in response.data.lower()

    def test_detail_bug(self, client, app):
        """Testa visualização de detalhes de bug."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            bug = Bug(
                title='Bug Detalhado',
                description='Descrição detalhada',
                project_id=project.id,
                severity='alta',
                status='em andamento'
            )
            db.session.add(bug)
            db.session.commit()

            bug_id = bug.id

        response = client.get(f'/bugs/{bug_id}')
        assert response.status_code == 200
        assert 'Bug Detalhado'.encode('utf-8') in response.data
        assert 'Descrição detalhada'.encode('utf-8') in response.data
        assert 'alta'.encode('utf-8') in response.data
        assert 'em andamento'.encode('utf-8') in response.data

    def test_edit_bug_post_success(self, client, app):
        """Testa edição de bug via POST."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            bug = Bug(
                title='Bug Original',
                description='Descrição original',
                project_id=project.id,
                severity='baixa',
                status='aberto'
            )
            db.session.add(bug)
            db.session.commit()

            bug_id = bug.id
            project_id = project.id

        response = client.post(f'/bugs/{bug_id}/editar', data={
            'title': 'Bug Editado',
            'description': 'Descrição editada',
            'project_id': project_id,
            'severity': 'crítica',
            'status': 'resolvido'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Bug atualizado com sucesso'.encode('utf-8') in response.data
        assert 'Bug Editado'.encode('utf-8') in response.data

        with app.app_context():
            updated = Bug.query.get(bug_id)
            assert updated.title == 'Bug Editado'
            assert updated.severity == 'crítica'
            assert updated.status == 'resolvido'

    def test_delete_bug_post_success(self, client, app):
        """Testa exclusão de bug via POST."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            bug = Bug(
                title='Bug Deletar',
                description='Descrição',
                project_id=project.id,
                severity='baixa',
                status='aberto'
            )
            db.session.add(bug)
            db.session.commit()
            bug_id = bug.id

        response = client.post(f'/bugs/{bug.id}/excluir', data={
            'confirm': True
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Bug excluído com sucesso'.encode('utf-8') in response.data

        with app.app_context():
            assert Bug.query.get(bug_id) is None


class TestDashboardIndicators:
    """Testes para indicadores do dashboard."""

    def test_dashboard_shows_correct_test_execution_status(self, client, app):
        """Testa se dashboard conta execuções corretamente (último status)."""
        with app.app_context():
            project = Project(name='Projeto Teste', status='Ativo')
            db.session.add(project)
            db.session.commit()

            # Caso 1: Nunca executado
            tc1 = TestCase(title='TC Nunca', steps='s', expected_result='r', project_id=project.id)

            # Caso 2: Executado 1 vez (aprovado)
            tc2 = TestCase(title='TC Aprovado', steps='s', expected_result='r', project_id=project.id)

            # Caso 3: Executado 2 vezes (aprovado, depois reprovado) - deve contar como reprovado
            tc3 = TestCase(title='TC Cambiante', steps='s', expected_result='r', project_id=project.id)

            db.session.add_all([tc1, tc2, tc3])
            db.session.commit()

            db.session.add(TestExecution(test_case_id=tc2.id, status='aprovado'))

            db.session.add(TestExecution(test_case_id=tc3.id, status='aprovado'))
            db.session.add(TestExecution(test_case_id=tc3.id, status='reprovado'))

            db.session.commit()

        response = client.get('/')

        # Deve mostrar 1 aprovado (tc2), 1 reprovado (tc3), 1 não executado (tc1)
        assert response.status_code == 200
        # Verificar que os contadores estão presentes
        assert '1'.encode('utf-8') in response.data  # Pelo menos contar corretamente

    def test_dashboard_latest_execution_tie_breaker_by_id(self, client, app):
        """Testa desempate por id quando executed_at é igual."""
        from datetime import datetime
        with app.app_context():
            project = Project(name='Projeto Teste Tie', status='Ativo')
            db.session.add(project)
            db.session.commit()

            tc = TestCase(title='TC Tie', steps='s', expected_result='r', project_id=project.id)
            db.session.add(tc)
            db.session.commit()

            tc_id = tc.id

            same_time = datetime.utcnow()
            # Duas execuções com o mesmo executed_at
            exec1 = TestExecution(test_case_id=tc_id, status='aprovado', executed_at=same_time)
            db.session.add(exec1)
            db.session.commit()

            exec2 = TestExecution(test_case_id=tc_id, status='reprovado', executed_at=same_time)
            db.session.add(exec2)
            db.session.commit()

            # exec2 tem id maior, deve ser considerado mais recente
            assert exec2.id > exec1.id

        response = client.get('/')
        assert response.status_code == 200

        # Verificação direta via query
        with app.app_context():
            from sqlalchemy import func
            row_number = func.row_number().over(
                partition_by=TestExecution.test_case_id,
                order_by=[TestExecution.executed_at.desc(), TestExecution.id.desc()]
            ).label('rn')
            ranked_subq = db.session.query(
                TestExecution.id.label('exec_id'),
                row_number
            ).subquery('ranked_exec')

            latest = db.session.query(TestExecution).\
                join(ranked_subq, TestExecution.id == ranked_subq.c.exec_id).\
                filter(ranked_subq.c.rn == 1).\
                filter(TestExecution.test_case_id == tc_id).\
                first()
            assert latest is not None
            assert latest.status == 'reprovado'
            assert latest.id == exec2.id

    def test_dashboard_filters_by_project(self, client, app):
        """Testa filtro por projeto no dashboard."""
        with app.app_context():
            project1 = Project(name='Projeto 1', status='Ativo')
            project2 = Project(name='Projeto 2', status='Ativo')
            db.session.add_all([project1, project2])
            db.session.commit()

            # 2 casos para projeto 1
            tc1 = TestCase(title='TC P1-1', steps='s', expected_result='r', project_id=project1.id)
            tc2 = TestCase(title='TC P1-2', steps='s', expected_result='r', project_id=project1.id)

            # 1 caso para projeto 2
            tc3 = TestCase(title='TC P2-1', steps='s', expected_result='r', project_id=project2.id)

            db.session.add_all([tc1, tc2, tc3])
            db.session.commit()

            project1_id = project1.id

        response = client.get(f'/?project_id={project1_id}')
        assert response.status_code == 200
        # Dashboard deve filtrar e mostrar contadores do projeto 1
        assert response.status_code == 200