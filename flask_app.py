#!/usr/bin/python
# Author: Justin


"""
Flask app drive module
"""


from flask import Flask, render_template
from bokeh.embed import autoload_server
from acquisition_app import AcquisitionAPP

app = Flask(__name__)

@app.route('/<app_name>')
def index(app_name):
    script = autoload_server(model=None, session_id = app_name)
    return render_template('index.html', bokeh_script=script)
