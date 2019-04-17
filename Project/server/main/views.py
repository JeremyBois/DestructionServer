# Project/server/main/views.py

import logging

from flask import render_template, Blueprint, request

from Project.tools.socketIO_blueprint import IOBlueprint
from Project.server.data import Host

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
def on_message(msg):
    """Server side event handler for an unnamed event using String messages."""
    mainIO_log.info('Unnamed String Event: {0} {1}'.format(msg, request.sid))


@mainIO_blueprint.on('json')
def on_json(json: dict):
    """Server side event handler for an unnamed event using JSON messages."""
    mainIO_log.info('Unnamed JSON Event: {0} {1}'.format(str(json), request.sid))


@mainIO_blueprint.on('connect')
def on_connect():
    ipAddress = ''
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ipAddress = request.remote_addr
    else:
        # If behind a proxy
        ipAddress = request.environ['HTTP_X_FORWARDED_FOR']
        template = 'Client behind proxy (HTTP_X_REAL_IP={0}, HTTP_X_FORWARDED_FOR={1}'
        mainIO_log.info(template.format(request.environ.get('HTTP_X_REAL_IP'),
                                        ipAddress))

    # Register new client with associated session ID
    client = container.register_client(request.sid, ipAddress,
                                       request.event['args'][0]['REMOTE_PORT'])
    mainIO_log.info('Client {0} now connected {1}:{2} '.format(client.sid, client.adrr, client.port))


@mainIO_blueprint.on('disconnect')
def on_disconnect():
    # Try removing it from host list in case client game not shutdown properly
    container.remove_host_by_ID(request.sid)
    mainIO_log.debug('Container updated (DEL -> {0})'.format(len(container.hosts)))

    # Unregister new client
    client = container.unregister_client(request.sid)
    if client is not None:
        mainIO_log.info('Client {0} now disconnected {1}:{2} '.format(client.sid, client.adrr, client.port))


@mainIO_blueprint.on(OnAddHost)
def on_add_host(json: dict):
    """Event send when a client start hosting."""
    json['ipAddress'] = container.clients[request.sid].adrr
    container.add_host(Host.from_dict(json, request.sid))
    mainIO_log.info('Container updated (ADD -> {0})'.format(len(container.hosts)))


@mainIO_blueprint.on(OnAskHosts)
def on_ask_hosts(msg: str):
    """Event send when a client ask for hosts list."""
    hosts = container.hosts_as_json()
    emit(OnHostsList, hosts, broadcast=False, json=True)
    mainIO_log.info('{0} asking for hosts'.format(request.sid))


@mainIO_blueprint.on(OnRemoveHost)
def on_remove_host(json: dict):
    """Event send when a client stop hosting."""
    container.remove_host_by_ID(request.sid)
    mainIO_log.info('Container updated (DEL -> {0})'.format(len(container.hosts)))


@mainIO_blueprint.on(OnUpdateHostConnection)
def on_updateConnection_host(json: dict):
    """Update data connection informations about an host"""
    target_host = Host.from_dict(json)
    updatedHost = container.update_open_connections(target_host)
    if (updatedHost):
        # Should notify other ??
        emit(OnUpdateHostSucceeded, json, broadcast=False, json=True)
        mainIO_log.info('Host updated {0}'.format(updatedHost))
    else:
        emit(OnUpdateHostFailed, json, broadcast=False, json=True)
        mainIO_log.warning('Host not updated {0}'.format(target_host))


@mainIO_blueprint.on(OnJoinSuceeded)
def on_clientJoin_success(msg):
    mainIO_log.info('Client {0} (name = {1}) has join game'.format(request.sid, msg))


# Get public ip
# import urllib.request
# ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

# Get informations about event
# print(request.event)
