from flask import Blueprint

Dashboard = Blueprint("Dashboard", __name__)
from . import routes