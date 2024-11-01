from flask import Blueprint

User = Blueprint("User", __name__)
from . import routes