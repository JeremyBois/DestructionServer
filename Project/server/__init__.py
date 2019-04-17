# Project/server/__init__.py


# Flask
from flask import Flask, render_template

# SocketIO
from flask_socketio import SocketIO

# Crypto
from flask_bcrypt import Bcrypt

# Jinja filters
from . import jinjafilter

# Data storage
from Project.server.data import DataManager

# Control server terminate at exit
from Project.server.hole_punching import RendezVousServerUDP
from werkzeug.serving import is_running_from_reloader


import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Create a NullHandler."""

        def emit(self, record):
            pass

# Assign NullHandler as default root handler
LOG = 'DestructServer'
server_log = logging.getLogger(LOG)
server_log.addHandler(logging.NullHandler())


# Extensions
bcrypt = Bcrypt()

# Data storage
container = DataManager()
container.init_app(LOG)

# UDP
udpServer = RendezVousServerUDP()


def create_app(environnement: str = 'dev'):
    """Initialize the application. Environnement can be 'dev', 'testing', 'prod', 'prod_pythonanywhere'."""
    app = Flask(__name__, template_folder='../client/templates', static_folder="../client/static")
    app.config.from_object('Project.server._config.DevelopmentConfig')

    mapper = {'testing': 'Project.server._config.TestingConfig',
              'prod': 'Project.server._config.ProductionConfig',
              'prod_pythonanywhere': 'Project.server._config.ProductionPythonAnywhereConfig'}

    environnement = environnement.lower()
    if environnement in mapper.keys():
        app.config.from_object(mapper[environnement])

    # Attach extensions
    jinjafilter.init_app(app)
    bcrypt.init_app(app)

    # Register our blueprints
    from Project.server.main.views import main_blueprint
    app.register_blueprint(main_blueprint)

    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template('errors/500.html'), 500

    # SocketIO support
    socketio = SocketIO(app)

    from Project.server.main.views import mainIO_blueprint
    mainIO_blueprint.init_io(socketio)

    # UDP server should only be run once
    if (not is_running_from_reloader()):
        udpServer.start('localhost', 5000)

    return app, socketio, udpServer
