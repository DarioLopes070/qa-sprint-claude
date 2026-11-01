from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from qa_sprint.models import Project


class ProjectForm(FlaskForm):
    name = StringField(
        'Nome',
        validators=[DataRequired(message='Nome é obrigatório.'), Length(max=120, message='Nome deve ter no máximo 120 caracteres.')],
        render_kw={'class': 'form-control', 'placeholder': 'Nome do projeto'}
    )
    description = TextAreaField(
        'Descrição',
        validators=[Optional(), Length(max=2000, message='Descrição deve ter no máximo 2000 caracteres.')],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrição do projeto (opcional)'}
    )
    status = SelectField(
        'Status',
        choices=[('Ativo', 'Ativo'), ('Arquivado', 'Arquivado')],
        validators=[DataRequired(message='Status é obrigatório.')],
        render_kw={'class': 'form-select'}
    )
    submit = SubmitField('Salvar', render_kw={'class': 'btn btn-primary'})

    def validate_name(self, field):
        name = field.data.strip() if field.data else ''
        if not name:
            raise ValidationError('Nome é obrigatório.')
        if len(name) > 120:
            raise ValidationError('Nome deve ter no máximo 120 caracteres.')
        # Verifica unicidade (exceto na edição)
        existing = Project.query.filter(Project.name == name)
        if hasattr(self, 'project_id') and self.project_id:
            existing = existing.filter(Project.id != self.project_id)
        if existing.first():
            raise ValidationError('Já existe um projeto com este nome.')

    def validate_status(self, field):
        if field.data not in Project.VALID_STATUSES:
            raise ValidationError(f"Status inválido. Valores permitidos: {', '.join(Project.VALID_STATUSES)}")


class DeleteConfirmForm(FlaskForm):
    confirm = SubmitField('Confirmar exclusão', render_kw={'class': 'btn btn-danger'})
    cancel = SubmitField('Cancelar', render_kw={'class': 'btn btn-secondary'})