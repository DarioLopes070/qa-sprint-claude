from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from qa_sprint.models import Project, TestCase, TestExecution


class TestCaseForm(FlaskForm):
    title = StringField(
        'Título',
        validators=[DataRequired(message='Título é obrigatório.'), Length(max=200, message='Título deve ter no máximo 200 caracteres.')],
        render_kw={'class': 'form-control', 'placeholder': 'Título do caso de teste'}
    )
    steps = TextAreaField(
        'Passos de Execução',
        validators=[DataRequired(message='Passos de execução são obrigatórios.')],
        render_kw={'class': 'form-control', 'rows': 6, 'placeholder': 'Descreva os passos para executar o teste'}
    )
    expected_result = TextAreaField(
        'Resultado Esperado',
        validators=[DataRequired(message='Resultado esperado é obrigatório.')],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o resultado esperado'}
    )
    project_id = SelectField(
        'Projeto',
        coerce=int,
        validators=[DataRequired(message='Projeto é obrigatório.')],
        render_kw={'class': 'form-select'}
    )
    submit = SubmitField('Salvar', render_kw={'class': 'btn btn-primary'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id.choices = [(p.id, p.name) for p in Project.query.filter_by(status='Ativo').order_by(Project.name).all()]

    def validate_title(self, field):
        title = field.data.strip() if field.data else ''
        if not title:
            raise ValidationError('Título é obrigatório.')
        if len(title) > 200:
            raise ValidationError('Título deve ter no máximo 200 caracteres.')

    def validate_steps(self, field):
        if not field.data or not field.data.strip():
            raise ValidationError('Passos de execução são obrigatórios.')

    def validate_expected_result(self, field):
        if not field.data or not field.data.strip():
            raise ValidationError('Resultado esperado é obrigatório.')


class TestCaseDeleteForm(FlaskForm):
    confirm = SubmitField('Confirmar exclusão', render_kw={'class': 'btn btn-danger'})
    cancel = SubmitField('Cancelar', render_kw={'class': 'btn btn-secondary'})


class TestExecutionForm(FlaskForm):
    test_case_id = HiddenField('TestCase ID')
    status = SelectField(
        'Status',
        choices=[('aprovado', 'Aprovado'), ('reprovado', 'Reprovado'), ('bloqueado', 'Bloqueado')],
        validators=[DataRequired(message='Status é obrigatório.')],
        render_kw={'class': 'form-select'}
    )
    observations = TextAreaField(
        'Observações',
        validators=[Optional(), Length(max=2000, message='Observações deve ter no máximo 2000 caracteres.')],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'Observações sobre a execução (opcional)'}
    )
    submit = SubmitField('Registrar', render_kw={'class': 'btn btn-success'})

    def validate_status(self, field):
        if field.data not in TestExecution.VALID_STATUSES:
            raise ValidationError(f"Status inválido. Valores permitidos: {', '.join(TestExecution.VALID_STATUSES)}")