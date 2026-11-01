from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from qa_sprint.models import Project, Bug


class BugForm(FlaskForm):
    title = StringField(
        'Título',
        validators=[DataRequired(message='Título é obrigatório.'), Length(max=200, message='Título deve ter no máximo 200 caracteres.')],
        render_kw={'class': 'form-control', 'placeholder': 'Título do bug'}
    )
    description = TextAreaField(
        'Descrição',
        validators=[DataRequired(message='Descrição é obrigatória.')],
        render_kw={'class': 'form-control', 'rows': 6, 'placeholder': 'Descreva o bug detalhadamente'}
    )
    project_id = SelectField(
        'Projeto',
        coerce=int,
        validators=[DataRequired(message='Projeto é obrigatório.')],
        render_kw={'class': 'form-select'}
    )
    severity = SelectField(
        'Severidade',
        choices=[('baixa', 'Baixa'), ('média', 'Média'), ('alta', 'Alta'), ('crítica', 'Crítica')],
        validators=[DataRequired(message='Severidade é obrigatória.')],
        render_kw={'class': 'form-select'}
    )
    status = SelectField(
        'Status',
        choices=[('aberto', 'Aberto'), ('em andamento', 'Em Andamento'), ('resolvido', 'Resolvido')],
        validators=[DataRequired(message='Status é obrigatório.')],
        render_kw={'class': 'form-select'}
    )
    submit = SubmitField('Salvar', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id.choices = [(p.id, p.name) for p in Project.query.filter_by(status='Ativo').order_by(Project.name).all()]
        if not self.severity.data:
            self.severity.data = 'baixa'
        if not self.status.data:
            self.status.data = 'aberto'

    def validate_title(self, field):
        title = field.data.strip() if field.data else ''
        if not title:
            raise ValidationError('Título é obrigatório.')
        if len(title) > 200:
            raise ValidationError('Título deve ter no máximo 200 caracteres.')

    def validate_description(self, field):
        if not field.data or not field.data.strip():
            raise ValidationError('Descrição é obrigatória.')

    def validate_severity(self, field):
        if field.data not in Bug.VALID_SEVERITIES:
            raise ValidationError(f"Severidade inválida. Valores permitidos: {', '.join(Bug.VALID_SEVERITIES)}")

    def validate_status(self, field):
        if field.data not in Bug.VALID_STATUSES:
            raise ValidationError(f"Status inválido. Valores permitidos: {', '.join(Bug.VALID_STATUSES)}")


class BugDeleteForm(FlaskForm):
    confirm = SubmitField('Confirmar exclusão', render_kw={'class': 'btn btn-danger'})
    cancel = SubmitField('Cancelar', render_kw={'class': 'btn btn-secondary'})