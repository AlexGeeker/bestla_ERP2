from flask import Blueprint
main = Blueprint('main', __name__, static_folder='../static', static_url_path='/')
from . import errors,views