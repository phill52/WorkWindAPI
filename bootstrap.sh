#!/bin/bash
export FLASK_APP=app.py
pipenv run flask --app main run -h 0.0.0.0
  