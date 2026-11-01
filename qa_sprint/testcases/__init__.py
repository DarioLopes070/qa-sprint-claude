from flask import Blueprint

testcases_bp = Blueprint('testcases', __name__, url_prefix='/testcases')

from qa_sprint.testcases import routes  # noqa: F401