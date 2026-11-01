from flask import Blueprint, render_template, abort, request
from sqlalchemy import func
from qa_sprint.models import Project, TestCase, TestExecution, Bug
from qa_sprint.main.forms import EmptyForm
from qa_sprint.main import main_bp
from qa_sprint.extensions import db


@main_bp.route('/')
def dashboard():
    project_id = request.args.get('project_id', type=int)

    # Projects
    total_projects = Project.get_total_count()
    active_projects = Project.get_active_count()

    # Test Cases
    test_cases_query = TestCase.query
    if project_id:
        test_cases_query = test_cases_query.filter_by(project_id=project_id)
    total_test_cases = test_cases_query.count()

    # Test Executions - count only latest execution per TestCase
    # Use window function to guarantee one execution per TestCase, tie-breaking by id
    row_number = func.row_number().over(
        partition_by=TestExecution.test_case_id,
        order_by=[TestExecution.executed_at.desc(), TestExecution.id.desc()]
    ).label('rn')

    ranked_subq = db.session.query(
        TestExecution.id.label('exec_id'),
        row_number
    ).subquery('ranked_exec')

    base_execs_query = db.session.query(TestExecution).\
        join(ranked_subq, TestExecution.id == ranked_subq.c.exec_id).\
        filter(ranked_subq.c.rn == 1).\
        join(TestCase, TestCase.id == TestExecution.test_case_id)

    if project_id:
        base_execs_query = base_execs_query.filter(TestCase.project_id == project_id)

    passed_count = base_execs_query.filter(TestExecution.status == 'aprovado').count()
    failed_count = base_execs_query.filter(TestExecution.status == 'reprovado').count()
    blocked_count = base_execs_query.filter(TestExecution.status == 'bloqueado').count()

    executed_test_cases_q = db.session.query(TestExecution.test_case_id).\
        join(ranked_subq, TestExecution.id == ranked_subq.c.exec_id).\
        filter(ranked_subq.c.rn == 1).\
        join(TestCase, TestCase.id == TestExecution.test_case_id)
    if project_id:
        executed_test_cases_q = executed_test_cases_q.filter(TestCase.project_id == project_id)
    executed_test_cases_count = executed_test_cases_q.distinct().count()
    not_executed_count = total_test_cases - executed_test_cases_count

    # Bugs
    bugs_query = Bug.query
    if project_id:
        bugs_query = bugs_query.filter_by(project_id=project_id)
    total_bugs = bugs_query.count()
    bugs_open = bugs_query.filter_by(status='aberto').count()
    bugs_in_progress = bugs_query.filter_by(status='em andamento').count()
    bugs_resolved = bugs_query.filter_by(status='resolvido').count()

    # Bugs by severity
    bugs_by_severity = {}
    for severity in Bug.VALID_SEVERITIES:
        sev_query = Bug.query
        if project_id:
            sev_query = sev_query.filter_by(project_id=project_id)
        bugs_by_severity[severity] = sev_query.filter_by(severity=severity).count()

    # Projects for filter
    projects = Project.query.filter_by(status='Ativo').order_by(Project.name).all()

    form = EmptyForm()
    return render_template(
        'dashboard.html',
        total_projects=total_projects,
        active_projects=active_projects,
        total_test_cases=total_test_cases,
        passed_count=passed_count,
        failed_count=failed_count,
        blocked_count=blocked_count,
        not_executed_count=not_executed_count,
        total_bugs=total_bugs,
        bugs_open=bugs_open,
        bugs_in_progress=bugs_in_progress,
        bugs_resolved=bugs_resolved,
        bugs_by_severity=bugs_by_severity,
        projects=projects,
        selected_project=project_id,
        form=form
    )


@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    from qa_sprint.extensions import db
    db.session.rollback()
    return render_template('500.html'), 500