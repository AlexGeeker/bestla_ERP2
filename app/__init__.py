# -*- coding: utf-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import config
from flask_sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()
moment = Moment()
dbs = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    # 使用本地bootstrap
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    dbs.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app