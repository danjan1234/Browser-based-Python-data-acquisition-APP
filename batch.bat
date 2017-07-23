@echo off
start cmd /k bokeh serve --host localhost:5000 --host localhost:5006
start cmd /k python example_apps.py
set FLASK_APP=flask_app.py
start cmd /k flask run