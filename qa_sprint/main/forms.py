from flask_wtf import FlaskForm
from wtforms import SubmitField


class EmptyForm(FlaskForm):
    """Formulário vazio apenas para CSRF em ações simples."""
    pass