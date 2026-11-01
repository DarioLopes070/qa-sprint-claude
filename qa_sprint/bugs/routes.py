from flask import render_template, redirect, url_for, flash, request, abort
from qa_sprint.extensions import db
from qa_sprint.models import Project, Bug
from qa_sprint.bugs.forms import BugForm, BugDeleteForm
from qa_sprint.bugs import bugs_bp


@bugs_bp.route('/')
def list():
    project_id = request.args.get('project_id', type=int)
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Bug.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if severity_filter:
        query = query.filter_by(severity=severity_filter)

    pagination = query.order_by(Bug.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    bugs = pagination.items

    projects = Project.query.filter_by(status='Ativo').order_by(Project.name).all()
    return render_template(
        'bugs/list.html',
        bugs=bugs,
        pagination=pagination,
        projects=projects,
        selected_project=project_id,
        selected_status=status_filter,
        selected_severity=severity_filter
    )


@bugs_bp.route('/novo', methods=['GET', 'POST'])
def create():
    form = BugForm()
    if form.validate_on_submit():
        bug = Bug(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            project_id=form.project_id.data,
            severity=form.severity.data,
            status=form.status.data
        )
        errors = bug.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.add(bug)
            db.session.commit()
            flash('Bug criado com sucesso!', 'success')
            return redirect(url_for('bugs.detail', bug_id=bug.id))
    return render_template('bugs/create.html', form=form)


@bugs_bp.route('/<int:bug_id>')
def detail(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    form_delete = BugDeleteForm()
    return render_template('bugs/detail.html', bug=bug, form_delete=form_delete)


@bugs_bp.route('/<int:bug_id>/editar', methods=['GET', 'POST'])
def edit(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    form = BugForm(obj=bug)

    if form.validate_on_submit():
        bug.title = form.title.data.strip()
        bug.description = form.description.data.strip()
        bug.project_id = form.project_id.data
        bug.severity = form.severity.data
        bug.status = form.status.data

        errors = bug.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.commit()
            flash('Bug atualizado com sucesso!', 'success')
            return redirect(url_for('bugs.detail', bug_id=bug.id))

    return render_template('bugs/edit.html', form=form, bug=bug)


@bugs_bp.route('/<int:bug_id>/excluir', methods=['GET', 'POST'])
def delete(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    form = BugDeleteForm()

    if request.method == 'GET':
        return render_template('bugs/delete.html', bug=bug, form=form)

    if form.validate_on_submit():
        if form.confirm.data:
            db.session.delete(bug)
            db.session.commit()
            flash('Bug excluído com sucesso!', 'success')
            return redirect(url_for('bugs.list'))
        elif form.cancel.data:
            return redirect(url_for('bugs.detail', bug_id=bug.id))

    return render_template('bugs/delete.html', bug=bug, form=form)