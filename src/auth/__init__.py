from flask import Blueprint

bp = Blueprint('auth', __name__)

from src.auth import forms, routes
