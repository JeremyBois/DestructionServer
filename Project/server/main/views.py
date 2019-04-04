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
def handle_message(message):
    print('received message: ' + message)


@mainIO_blueprint.on('json')
def handle_json(json):
    print('received json: ' + str(json))


@mainIO_blueprint.on('MyEvent')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
