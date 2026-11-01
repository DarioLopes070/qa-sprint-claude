from flask import Blueprint

main_bp = Blueprint('main', __name__, template_folder='templates')

from qa_sprint.main import routes  # noqa: F401