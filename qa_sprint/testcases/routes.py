from flask import render_template, redirect, url_for, flash, request, abort
from qa_sprint.extensions import db
from qa_sprint.models import Project, TestCase, TestExecution
from qa_sprint.testcases.forms import TestCaseForm, TestCaseDeleteForm, TestExecutionForm
from qa_sprint.testcases import testcases_bp


@testcases_bp.route('/')
def list():
    project_id = request.args.get('project_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = TestCase.query
    if project_id:
        query = query.filter_by(project_id=project_id)

    pagination = query.order_by(TestCase.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    test_cases = pagination.items

    projects = Project.query.filter_by(status='Ativo').order_by(Project.name).all()
    return render_template(
        'testcases/list.html',
        test_cases=test_cases,
        pagination=pagination,
        projects=projects,
        selected_project=project_id
    )


@testcases_bp.route('/novo', methods=['GET', 'POST'])
def create():
    form = TestCaseForm()
    if form.validate_on_submit():
        test_case = TestCase(
            title=form.title.data.strip(),
            steps=form.steps.data.strip(),
            expected_result=form.expected_result.data.strip(),
            project_id=form.project_id.data
        )
        errors = test_case.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.add(test_case)
            db.session.commit()
            flash('Caso de teste criado com sucesso!', 'success')
            return redirect(url_for('testcases.detail', test_case_id=test_case.id))
    return render_template('testcases/create.html', form=form)


@testcases_bp.route('/<int:test_case_id>')
def detail(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)
    form_delete = TestCaseDeleteForm()
    execution_form = TestExecutionForm()
    execution_form.test_case_id.data = test_case_id
    return render_template(
        'testcases/detail.html',
        test_case=test_case,
        form_delete=form_delete,
        execution_form=execution_form
    )


@testcases_bp.route('/<int:test_case_id>/editar', methods=['GET', 'POST'])
def edit(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)
    form = TestCaseForm(obj=test_case)

    if form.validate_on_submit():
        test_case.title = form.title.data.strip()
        test_case.steps = form.steps.data.strip()
        test_case.expected_result = form.expected_result.data.strip()
        test_case.project_id = form.project_id.data

        errors = test_case.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.commit()
            flash('Caso de teste atualizado com sucesso!', 'success')
            return redirect(url_for('testcases.detail', test_case_id=test_case.id))

    return render_template('testcases/edit.html', form=form, test_case=test_case)


@testcases_bp.route('/<int:test_case_id>/excluir', methods=['GET', 'POST'])
def delete(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)
    form = TestCaseDeleteForm()

    if request.method == 'GET':
        return render_template('testcases/delete.html', test_case=test_case, form=form)

    if form.validate_on_submit():
        if form.confirm.data:
            db.session.delete(test_case)
            db.session.commit()
            flash('Caso de teste excluído com sucesso!', 'success')
            return redirect(url_for('testcases.list'))
        elif form.cancel.data:
            return redirect(url_for('testcases.detail', test_case_id=test_case.id))

    return render_template('testcases/delete.html', test_case=test_case, form=form)


@testcases_bp.route('/<int:test_case_id>/executar', methods=['POST'])
def execute(test_case_id):
    test_case = TestCase.query.get_or_404(test_case_id)
    form = TestExecutionForm()

    if form.validate_on_submit():
        execution = TestExecution(
            test_case_id=test_case.id,
            status=form.status.data,
            observations=form.observations.data.strip() if form.observations.data else None
        )
        errors = execution.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.add(execution)
            db.session.commit()
            flash('Execução registrada com sucesso!', 'success')
            return redirect(url_for('testcases.detail', test_case_id=test_case.id))

    return redirect(url_for('testcases.detail', test_case_id=test_case.id))