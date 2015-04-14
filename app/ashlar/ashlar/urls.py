from flask import Flask

import views
from views import hello

hello.add_url_rule('/', view_func=views.index, methods=['GET'])
