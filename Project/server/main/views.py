# Project/server/main/views.py


from flask import render_template, Blueprint

from Project.tools.socketIO_blueprint import IOBlueprint
# from flask_socketio import emit


main_blueprint = Blueprint('main', __name__,)
mainIO_blueprint = IOBlueprint('/')


@main_blueprint.route('/')
def home():
    return render_template('home.html')


@mainIO_blueprint.on('message')
def handle_messages(msg):
    """Server side event handler for an unnamed event using String messages."""
    print('Unnamed String Event: ' + msg)


@mainIO_blueprint.on('json')
def handle_json(json):
    """Server side event handler for an unnamed event using JSON messages."""
    print('Unnamed JSON Event: ' + str(json))


# HOST

@mainIO_blueprint.on('OnAddHost')
def handle_add_host(json):
    """Event send when a client start hosting."""
    print('New host available: ')


@mainIO_blueprint.on('OnRemoveHost')
def handle_remove_host(json):
    """Event send when a client stop hosting."""
    print('Losing an host: ')


# @TEST


@mainIO_blueprint.on('MyEvent')
def handle_basic_event(json):
    print('received json: ' + str(json))


# @mainIO_blueprint.on('MyJsonEvent')
# def handle_MyJsonEvent(json):
#     print('MyJsonEvent: ' + str(json))
