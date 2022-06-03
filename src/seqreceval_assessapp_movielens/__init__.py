from flask import Flask

from . import config
from .commands import custom_cli
from .extensions import extensions
from .extensions.database import db
from .views import blueprints


__version__ = '0.1.0'


def create_app(config_dict=None, config_file_path=None):
    app = Flask(__name__, instance_relative_config=True)

    _register_configurations(app, config_dict, config_file_path)
    _register_commands(app)
    _register_blueprints(app)
    _register_extensions(app)

    @app.route("/hello-world")
    def hello_world():
        return "Hello, World!"

    with app.app_context():
        db.create_all()

    return app


def _register_configurations(app, config_dict, config_file_path):
    app.config.from_object(config)

    if config_dict:
        app.config.from_mapping(config_dict)
    elif config_file_path:
        app.config.from_pyfile(config_file_path)
    else:
        app.config.from_pyfile('config.py', silent=True)


def _register_commands(app):
    app.cli.add_command(custom_cli)


def _register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)


def _register_extensions(app):
    for ext in extensions:
        ext.init_app(app)
