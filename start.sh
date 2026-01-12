#!/bin/bash
export FLASK_APP=main.py
export FLASK_ENV=production
gunicorn main:app
