from flask import Blueprint, render_template, abort
from qa_sprint.models import Project
from qa_sprint.main.forms import EmptyForm
from qa_sprint.main import main_bp


@main_bp.route('/')
def dashboard():
    total_projects = Project.get_total_count()
    active_projects = Project.get_active_count()
    form = EmptyForm()
    return render_template(
        'dashboard.html',
        total_projects=total_projects,
        active_projects=active_projects,
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