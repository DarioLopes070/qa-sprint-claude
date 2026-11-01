from flask import render_template, redirect, url_for, flash, request, abort
from qa_sprint.extensions import db
from qa_sprint.models import Project
from qa_sprint.projects.forms import ProjectForm, DeleteConfirmForm
from qa_sprint.projects import projects_bp


@projects_bp.route('/')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Project.query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    projects = pagination.items
    form = DeleteConfirmForm()
    return render_template('projects/list.html', projects=projects, pagination=pagination, form=form)


@projects_bp.route('/novo', methods=['GET', 'POST'])
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            status=form.status.data
        )
        errors = project.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.add(project)
            db.session.commit()
            flash('Projeto criado com sucesso!', 'success')
            return redirect(url_for('projects.detail', project_id=project.id))
    return render_template('projects/create.html', form=form)


@projects_bp.route('/<int:project_id>')
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    form = DeleteConfirmForm()
    return render_template('projects/detail.html', project=project, form=form)


@projects_bp.route('/<int:project_id>/editar', methods=['GET', 'POST'])
def edit(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    form.project_id = project_id  # Para validação de unicidade na edição

    if form.validate_on_submit():
        project.name = form.name.data.strip()
        project.description = form.description.data.strip() if form.description.data else None
        project.status = form.status.data

        errors = project.validate()
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            db.session.commit()
            flash('Projeto atualizado com sucesso!', 'success')
            return redirect(url_for('projects.detail', project_id=project.id))

    return render_template('projects/edit.html', form=form, project=project)


@projects_bp.route('/<int:project_id>/excluir', methods=['GET', 'POST'])
def delete(project_id):
    project = Project.query.get_or_404(project_id)
    form = DeleteConfirmForm()

    if request.method == 'GET':
        # GET apenas exibe a confirmação
        return render_template('projects/delete.html', project=project, form=form)

    # POST processa a exclusão
    if form.validate_on_submit():
        if form.confirm.data:
            db.session.delete(project)
            db.session.commit()
            flash('Projeto excluído com sucesso!', 'success')
            return redirect(url_for('projects.list'))
        elif form.cancel.data:
            return redirect(url_for('projects.detail', project_id=project.id))

    return render_template('projects/delete.html', project=project, form=form)