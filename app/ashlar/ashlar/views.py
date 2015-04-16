from flask import Blueprint

hello = Blueprint('hello', __name__)

def index():
    return 'Yo, world!'
