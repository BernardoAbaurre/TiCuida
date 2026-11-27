#!/bin/sh
# Cria/atualiza o banco, carrega os dados de demonstração (idempotente) e sobe a API.
set -e
export FLASK_APP=app.py
flask db upgrade
flask seed
exec gunicorn wsgi:app --bind "0.0.0.0:${PORT:-8000}" --workers 2 --access-logfile -
