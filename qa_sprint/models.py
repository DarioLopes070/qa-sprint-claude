from datetime import datetime
from qa_sprint.extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    VALID_STATUSES = ['Ativo', 'Arquivado']

    def __repr__(self):
        return f'<Project {self.name}>'

    def validate(self):
        """Valida os dados do projeto. Retorna lista de erros (vazio se válido)."""
        errors = []

        # Nome: obrigatório, até 120 chars, sem espaços nas extremidades
        if not self.name or not self.name.strip():
            errors.append('Nome é obrigatório.')
        else:
            self.name = self.name.strip()
            if len(self.name) > 120:
                errors.append('Nome deve ter no máximo 120 caracteres.')

        # Status: deve ser válido
        if self.status not in self.VALID_STATUSES:
            errors.append(f"Status inválido. Valores permitidos: {', '.join(self.VALID_STATUSES)}")

        return errors

    @classmethod
    def get_active_count(cls):
        return cls.query.filter_by(status='Ativo').count()

    @classmethod
    def get_total_count(cls):
        return cls.query.count()