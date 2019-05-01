# Project/destruck_server.py

from Project.server.hole_punching.server import RendezVousServerUDP

import socket
import logging
import json
import time

# Static typing checking
from typing import Tuple, Dict, Any


class DestruckUDPServer(RendezVousServerUDP):

    # Byte size used to store FString (Unreal)
    INT32_SIZE = 4
    ORIGIN_SERVER = 'UDPServer'
    ORIGIN_CLIENT = 'Client'
    ORIGIN_HOST = 'Host'

    """Concrete implementation of a Rendezvous server to handle
       UDP hole punching for Unreal game Destruction.
    """

    def __init__(self, encoding: str = 'utf-8'):
        """
            Init server socket and data encoding used.
        """
        super().__init__(encoding=encoding)

        # Store informations about a specific host
        self.unreal_hosts = {}

    def _handle_client(self, sock: socket.socket, addr: Tuple[str, int], data: bytes):
        self._logger.info('Receive data from {0}:{1}.'.format(addr[0], str(addr[1])))

        # Assume data comes from Unreal game instance where strings are length prefixed
        msg = data[DestruckUDPServer.INT32_SIZE:].decode(self._encoding)
        self._logger.debug('Receive message :: {0}.'.format(msg))

        # Accept JSON or raw string
        if msg[0] == '{':
            self._handle_json_msg(sock, addr, json.loads(msg))
        else:
            self._handle_string_msg(sock, addr, msg)

    def _handle_string_msg(self, sock: socket.socket, addr: Tuple[str, int], msg: str):
        # Send a JSON because Unreal client only understand JSON format
        msg_dict = {}
        msg_dict['Msg'] = 'Message received !'
        msg_dict['Origin'] = DestruckUDPServer.ORIGIN_SERVER
        self._send_msg(self._sock, msg_dict, addr)

    def _handle_json_msg(self, sock: socket.socket, addr: Tuple[str, int], msg: Dict):
        if msg['Origin'] == DestruckUDPServer.ORIGIN_CLIENT:
            # Message from Unreal client
            self._handle_unrealClient(sock, addr, msg)
        elif msg['Origin'] == DestruckUDPServer.ORIGIN_HOST:
            # Message from Unreal host
            self._handle_unrealHost(sock, addr, msg)

    def _handle_unrealHost(self, sock: socket.socket, addr: Tuple[str, int], json_data: Dict):
        # Only do something if request is correctly defined
        if (json_data.get('Request', None) == 'Register'):
            # Send back public informations back to Host
            msg = {}
            msg['IP'] = addr[0]
            msg['Port'] = addr[1]
            msg['Origin'] = DestruckUDPServer.ORIGIN_SERVER
            msg['Request'] = 'Register'
            self._send_msg(self._sock, msg, addr)
        # @Unreal --> Update public entrypoint and sent it to TCP server

    def _handle_unrealClient(self, sock: socket.socket, addr: Tuple[str, int], json_data: Dict):
        # Only do something if request is correctly defined
        if (json_data.get('Request', None) == 'Join'):
            # Send public entrypoint back to sender
            msg = {}
            msg['Request'] = 'Join'
            msg['IP'] = addr[0]
            msg['Port'] = addr[1]
            msg['HostIP'] = json_data['HostIP']
            msg['HostPort'] = json_data['HostPort']
            msg['Origin'] = DestruckUDPServer.ORIGIN_SERVER
            self._send_msg(sock, msg, addr)
            # @TODO Unreal side --> Hole punch through Host entrypoint

            # Server will not receive it that way
            # # Send peer public informations to Unreal host
            # msg = {}
            # msg['PeerIP'] = addr[0]
            # msg['PeerPort'] = addr[1]
            # msg['Origin'] = DestruckUDPServer.ORIGIN_SERVER
            # host_addr = (json_data['HostIP'], json_data['HostPort'])
            # # @TODO Unreal side --> Hole punch through Peer entrypoint
            # self._send_msg(sock, msg, host_addr)

    def _send_msg(self, sock: socket.socket, msg: Any, addr: Tuple[str, int]) -> None:
        template1 = 'Send message :: {0}.'
        template2 = 'Send message to {0}:{1} using interface {2}:{3}.'
        if (isinstance(msg, str)):
            msg_bytes = self.serialized_str(msg)
        elif (isinstance(msg, dict)):
            msg_bytes = self.serialized_str(json.dumps(msg))
        else:
            msg_bytes = msg

        # Send it !
        sock.sendto(msg_bytes, addr)
        self._logger.debug(template1.format(msg))
        self._logger.info(template2.format(addr[0], addr[1],
                                           *sock.getsockname()))

    def serialized_str(self, msg: str) -> bytes:
        """
            Return a bytes representation of a python str in FString serialized
            form (length prefixed).
        """
        # String in Unreal are length prefixed
        msg_string = msg.encode(self._encoding)
        msg_bytes = len(msg_string).to_bytes(DestruckUDPServer.INT32_SIZE,
                                             byteorder='big')
        msg_bytes += msg_string
        return msg_bytes


if __name__ == '__main__':
    # LOG
    from logger import add_stream_handler, add_file_handler
    # Minimal level for logs
    log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)
    file_handler = add_file_handler('DestruckUDPServer.log', parent='RendezVous',
                                    level=log_level, filemode='a')
    stream_handler = add_stream_handler(parent='RendezVous', level=log_level)

    # SERVER
    server = DestruckUDPServer()
    server.start('0.0.0.0', 5000)
    # Stay up x seconds
    time.sleep(100)
    # Stop server
    server.stop()
