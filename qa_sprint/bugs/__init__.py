from flask import Blueprint

bugs_bp = Blueprint('bugs', __name__, url_prefix='/bugs', template_folder='templates')

from qa_sprint.bugs import routes  # noqa: F401