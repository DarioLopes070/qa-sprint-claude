from flask import Blueprint

projects_bp = Blueprint('projects', __name__, url_prefix='/projetos', template_folder='templates')

from qa_sprint.projects import routes  # noqa: F401