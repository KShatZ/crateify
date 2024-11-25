from flask import Blueprint

Playlist = Blueprint("Playlist", __name__)
from . import routes