from datetime import datetime
from qa_sprint.extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacionamentos
    test_cases = db.relationship('TestCase', back_populates='project', cascade='all, delete-orphan')
    bugs = db.relationship('Bug', back_populates='project', cascade='all, delete-orphan')

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


class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    steps = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacionamentos
    project = db.relationship('Project', back_populates='test_cases')
    executions = db.relationship('TestExecution', back_populates='test_case', cascade='all, delete-orphan', order_by='desc(TestExecution.executed_at)')

    def __repr__(self):
        return f'<TestCase {self.title}>'

    def validate(self):
        """Valida os dados do caso de teste. Retorna lista de erros (vazio se válido)."""
        errors = []

        if not self.title or not self.title.strip():
            errors.append('Título é obrigatório.')
        else:
            self.title = self.title.strip()
            if len(self.title) > 200:
                errors.append('Título deve ter no máximo 200 caracteres.')

        if not self.steps or not self.steps.strip():
            errors.append('Passos de execução são obrigatórios.')
        else:
            self.steps = self.steps.strip()

        if not self.expected_result or not self.expected_result.strip():
            errors.append('Resultado esperado é obrigatório.')
        else:
            self.expected_result = self.expected_result.strip()

        if not self.project_id:
            errors.append('Projeto é obrigatório.')

        return errors

    @classmethod
    def get_total_count(cls):
        return cls.query.count()

    @classmethod
    def get_by_project(cls, project_id):
        return cls.query.filter_by(project_id=project_id).order_by(cls.created_at.desc()).all()

    def get_last_execution_status(self):
        """Retorna o último status de execução ou 'Não executado'."""
        if self.executions:
            return self.executions[0].status
        return 'Não executado'

    def get_last_execution(self):
        """Retorna a última execução ou None."""
        return self.executions[0] if self.executions else None


class TestExecution(db.Model):
    __tablename__ = 'test_executions'

    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    observations = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacionamentos
    test_case = db.relationship('TestCase', back_populates='executions')

    VALID_STATUSES = ['aprovado', 'reprovado', 'bloqueado']

    def __repr__(self):
        return f'<TestExecution {self.id} - {self.status}>'

    def validate(self):
        """Valida os dados da execução. Retorna lista de erros (vazio se válido)."""
        errors = []

        if not self.test_case_id:
            errors.append('Caso de teste é obrigatório.')

        if not self.status or self.status not in self.VALID_STATUSES:
            errors.append(f"Status inválido. Valores permitidos: {', '.join(self.VALID_STATUSES)}")

        return errors

    @classmethod
    def get_count_by_status(cls, status):
        return cls.query.join(TestCase).filter(cls.status == status).count()


class Bug(db.Model):
    __tablename__ = 'bugs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='aberto')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacionamentos
    project = db.relationship('Project', back_populates='bugs')

    VALID_SEVERITIES = ['baixa', 'média', 'alta', 'crítica']
    VALID_STATUSES = ['aberto', 'em andamento', 'resolvido']

    def __repr__(self):
        return f'<Bug {self.title}>'

    def validate(self):
        """Valida os dados do bug. Retorna lista de erros (vazio se válido)."""
        errors = []

        if not self.title or not self.title.strip():
            errors.append('Título é obrigatório.')
        else:
            self.title = self.title.strip()
            if len(self.title) > 200:
                errors.append('Título deve ter no máximo 200 caracteres.')

        if not self.description or not self.description.strip():
            errors.append('Descrição é obrigatória.')
        else:
            self.description = self.description.strip()

        if not self.project_id:
            errors.append('Projeto é obrigatório.')

        if self.severity not in self.VALID_SEVERITIES:
            errors.append(f"Severidade inválida. Valores permitidos: {', '.join(self.VALID_SEVERITIES)}")

        if self.status not in self.VALID_STATUSES:
            errors.append(f"Status inválido. Valores permitidos: {', '.join(self.VALID_STATUSES)}")

        return errors

    @classmethod
    def get_total_count(cls):
        return cls.query.count()

    @classmethod
    def get_by_project(cls, project_id):
        return cls.query.filter_by(project_id=project_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_count_by_status(cls, status):
        return cls.query.filter_by(status=status).count()

    @classmethod
    def get_count_by_severity(cls, severity):
        return cls.query.filter_by(severity=severity).count()