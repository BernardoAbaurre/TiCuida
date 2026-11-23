"""Migrações do banco com Flask-Migrate (Alembic)."""

from flask_migrate import Migrate

from ticuida.ext.db import db

migrate = Migrate()


def init_app(app):
    # render_as_batch permite ALTER TABLE no SQLite
    migrate.init_app(app, db, render_as_batch=True, compare_type=True)
