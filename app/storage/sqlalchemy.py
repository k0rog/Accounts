from flask_sqlalchemy import SQLAlchemy
from flask import Flask


db = SQLAlchemy()


def configure_db(app: Flask):
    db.init_app(app)

    return db
