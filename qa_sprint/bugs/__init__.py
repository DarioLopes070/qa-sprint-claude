from flask import Blueprint

bugs_bp = Blueprint('bugs', __name__, url_prefix='/bugs')

from qa_sprint.bugs import routes  # noqa: F401