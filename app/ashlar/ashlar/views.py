from flask import Blueprint, request, render_template, redirect
from ashlar import app

hello = Blueprint('hello', __name__)

def index():
    return 'Yo, world!'
