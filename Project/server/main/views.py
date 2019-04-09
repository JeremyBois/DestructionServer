# Project/server/main/views.py

import logging

from flask import render_template, Blueprint, request

from Project.tools.socketIO_blueprint import IOBlueprint
from Project.server.host import Host

from flask_socketio import send

from Project.server import container, LOG


main_blueprint = Blueprint('main', __name__,)
main_log = logging.getLogger(LOG)
mainIO_blueprint = IOBlueprint('/')
mainIO_log = logging.getLogger(LOG + '.IO')


@main_blueprint.route('/')
def home():
    return render_template('home.html')


@mainIO_blueprint.on('message')
def handle_messages(msg):
    """Server side event handler for an unnamed event using String messages."""
    print('Unnamed String Event: ' + msg)


@mainIO_blueprint.on('json')
def handle_json(json: dict):
    """Server side event handler for an unnamed event using JSON messages."""
    print('Unnamed JSON Event: ' + str(json))


# HOST

@mainIO_blueprint.on('OnAddHost')
def handle_add_host(json: dict):
    """Event send when a client start hosting."""

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        print("NO PROXY")
        print(request.remote_addr)
        json['ipAddress'] = request.remote_addr
    else:
        # If behind a proxy
        print("BEHIND PROXY")
        print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
        print(request.environ['HTTP_X_FORWARDED_FOR'])
        json['ipAddress'] = request.environ['HTTP_X_FORWARDED_FOR']

    print(json)
    container.add_host(Host.from_dict(json))
    print('Container updated (ADD -> {0}) : {1}'.format(len(container.hosts), container.hosts))


@mainIO_blueprint.on('OnAskHosts')
def handle_ask_hosts(msg: str):
    """Event send when a client ask for hosts list."""
    print("Asking for hosts")
    send('OnHostsList', container.hosts_as_json(), broadcast=False, json=True)


@mainIO_blueprint.on('OnRemoveHost')
def handle_remove_host(json: dict):
    """Event send when a client stop hosting."""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        print("NO PROXY")
        print(request.remote_addr)
        json['ipAddress'] = request.remote_addr
    else:
        # If behind a proxy
        print("BEHIND PROXY")
        print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
        print(request.environ['HTTP_X_FORWARDED_FOR'])
        json['ipAddress'] = request.environ['HTTP_X_FORWARDED_FOR']

    container.remove_hosts(json['hostName'], json['ipAddress'])
    print('Container updated (DEL -> {0}) : {1}'.format(len(container.hosts), container.hosts))
