# Project/server/jinjafilter/__init__.py

from flask import url_for


def init_app(app):
    """
        Register functions to use in jinja templating.
        See https://code.tutsplus.com/tutorials/templating-with-jinja2-in-flask-advanced--cms-25794
    """

    @app.context_processor
    def host_processor():
        def get_rootURL():
            return url_for('main.home', _external=True)
        return {'get_rootURL': get_rootURL}
