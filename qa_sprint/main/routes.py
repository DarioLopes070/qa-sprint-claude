from flask import Blueprint, render_template, abort, request
from qa_sprint.models import Project, TestCase, TestExecution, Bug
from qa_sprint.main.forms import EmptyForm
from qa_sprint.main import main_bp


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

    # Test Executions
    exec_query = TestExecution.query.join(TestCase)
    if project_id:
        exec_query = exec_query.filter(TestCase.project_id == project_id)
    total_executions = exec_query.count()
    passed_count = exec_query.filter(TestExecution.status == 'aprovado').count()
    failed_count = exec_query.filter(TestExecution.status == 'reprovado').count()
    blocked_count = exec_query.filter(TestExecution.status == 'bloqueado').count()
    not_executed_count = total_test_cases - exec_query.with_entities(TestExecution.test_case_id).distinct().count()

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