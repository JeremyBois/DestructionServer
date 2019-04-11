# Project/server/main/views.py

import logging

from flask import render_template, Blueprint, request

from Project.tools.socketIO_blueprint import IOBlueprint
from Project.server.host import Host

from flask_socketio import emit

from Project.server import container, LOG


main_blueprint = Blueprint('main', __name__,)
main_log = logging.getLogger(LOG)
mainIO_blueprint = IOBlueprint('/')
mainIO_log = logging.getLogger(LOG + '.IO')


# Host events
OnAddHost = 'OnAddHost'
OnRemoveHost = 'OnRemoveHost'

# Join events
OnAskHosts = 'OnAskHosts'
OnHostsList = 'OnHostsList'
OnJoinSuceeded = 'OnJoinSuceeded'

# Update events
OnUpdateHostConnection = 'OnUpdateHostConnection'
OnUpdateHostSucceeded = 'OnUpdateHostSucceeded'
OnUpdateHostFailed = 'OnUpdateHostFailed'


@main_blueprint.route('/')
def home():
    return render_template('home.html')


@mainIO_blueprint.on('message')
def handle_messages(msg):
    """Server side event handler for an unnamed event using String messages."""
    print('Unnamed String Event: ' + msg, request.sid)


@mainIO_blueprint.on('json')
def handle_json(json: dict):
    """Server side event handler for an unnamed event using JSON messages."""
    print('Unnamed JSON Event: ' + str(json), request.sid)


@mainIO_blueprint.on('disconnect')
def handle_disconnect():
    container.remove_host_by_ID(request.sid)
    print(request.sid, ':: disconnected')
    print('Container updated (DEL -> {0}) : {1}'.format(len(container.hosts), container.hosts))


@mainIO_blueprint.on(OnAddHost)
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

    container.add_host(Host.from_dict(json, request.sid))
    print('Container updated (ADD -> {0}) : {1}'.format(len(container.hosts), container.hosts))


@mainIO_blueprint.on(OnAskHosts)
def handle_ask_hosts(msg: str):
    """Event send when a client ask for hosts list."""
    print("Asking for hosts")
    hosts = container.hosts_as_json()
    emit(OnHostsList, hosts, broadcast=False, json=True)


@mainIO_blueprint.on(OnRemoveHost)
def handle_remove_host(json: dict):
    """Event send when a client stop hosting."""
    container.remove_host_by_ID(request.sid)
    print('Container updated (DEL -> {0}) : {1}'.format(len(container.hosts), container.hosts))


@mainIO_blueprint.on(OnUpdateHostConnection)
def handle_updateConnection_host(json: dict):
    """Update data connection informations about an host"""
    sender = Host.from_dict(json)
    print(request.sid, ':: ', sender)
    updatedHost = container.update_open_connections(sender)
    if (updatedHost):
        # Should notify other ??
        emit(OnUpdateHostSucceeded, json, broadcast=False, json=True)
    else:
        emit(OnUpdateHostFailed, json, broadcast=False, json=True)
    print(request.sid, ':: ', updatedHost)


@mainIO_blueprint.on(OnJoinSuceeded)
def handle_clientJoin_success(msg):
    print(request.sid, ':: has join a game ::', msg)
