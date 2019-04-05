# Project/server/main/views.py

import logging

from flask import render_template, Blueprint, request

from Project.tools.socketIO_blueprint import IOBlueprint

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
    container.add_host(json['hostName'], json['ipAddress'], json['unrealName'])
    print('Container updated (ADD -> {0}) : {1}'.format(len(container.hosts), container.hosts))


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


# @TEST


@mainIO_blueprint.on('MyEvent')
def handle_basic_event(json: dict):
    print('received json: ' + str(json))


# @mainIO_blueprint.on('MyJsonEvent')
# def handle_MyJsonEvent(json):
#     print('MyJsonEvent: ' + str(json))
