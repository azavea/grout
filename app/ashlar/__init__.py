#!/usr/bin/env python

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import Api

from ashlar import urls
from ashlar.views import hello as hello_module

# Define the WSGI application object
app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

# Any module inits that require app and db
# must be imported after app is defined above
from api import item_schema_bp, record_schema_bp
from api import status

app.register_blueprint(hello_module)
app.register_blueprint(item_schema_bp)
app.register_blueprint(record_schema_bp)

# Sample HTTP error handling
@app.errorhandler(status.HTTP_404_NOTFOUND)
def not_found(error):
    return render_template('404.html'), status.HTTP_404_NOTFOUND

