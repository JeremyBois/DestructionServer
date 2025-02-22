# Project/server/interface/rendez_vous.py

"""
    Multi threaded UDP server.
      - One thread to handle clients reception
      - One thread to handle clients response
"""


import time
import logging
import socket
import threading
import pickle


from queue import Queue

# Static typing checking
from typing import Tuple, List, Any

from Project.server import LOG


__all__ = ['RendezVousServerUDP']


class RendezVousServerUDP(object):

    """
        Multi threaded UDP server.
          - One thread to handle clients reception /response
          - One thread to send data added to message queue
    """

    def __init__(self, encoding: str = 'utf-8'):
        """
            Init server socket and data encoding used.
        """
        super().__init__()

        # Encoding used
        self._encoding = encoding

        # Assign logger
        self._logger = logging.getLogger(LOG + '.' + 'UDP')
        self._nameT = '{0}({2})::{1}'

        # Store global data
        self._running = False
        self._port = 0
        self._host = 'localhost'

        # Init UDP socket
        self._socketFamily = socket.AF_INET
        self._socketType = socket.SOCK_DGRAM
        self._sock = socket.socket(self._socketFamily, self._socketType, socket.IPPROTO_UDP)
        # Force reuse of a port
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Keep track of thread
        self._receiveThread = None      # type: Any
        self._dataThread = None         # type: Any

        # Data
        self._container = Queue()      # type: Queue[Tuple[str, Tuple[str, int]]]
        self.clients = list()          # type: List[Tuple[str, int]]

    def start(self, host: str, port: int) -> bool:
        """Start UDP server."""
        try:
            # Update port used
            self._port = port
            self._host = host
            self._bind()

            # Start thread to handle clients incoming messages
            self._receiveThread = threading.Thread(target=self._receive_loop,
                                                   name='Recv-Send')
            self._receiveThread.start()

            # Start thread to deals with data added to queue
            self._dataThread = threading.Thread(target=self._data_loop,
                                                name='Data')
            self._dataThread.start()

        except socket.error as err:
            self._sock.close()
            self._logger.fatal('Start failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)
            self._logger.debug('Socket now closed (port {0}).'.format(self._port))
            return False
        return True

    def stop(self) -> bool:
        """Stop UDP server."""
        if not self._running:
            self._logger.info('Rendez-vous server is not running')
            return False
        try:
            self._stop()
            # Wait for accept threads
            self._dataThread.join()
            self._receiveThread.join()
            # Clean
            self._reset()
        except socket.error as err:
            self._logger.fatal('Stop failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)
        finally:
            self._sock.close()
            self._logger.debug('Server socket now closed (port {0}).'.format(self._port))
            return True

    def _receive_loop(self) -> None:
        """Wait for incoming messages. Should run on a separated thread."""
        try:
            self._running = True
            while self._running:
                self._logger.debug('Waiting for connections.')
                # Wait for message (max size of 4096)
                msg, addr = self._sock.recvfrom(4096)

                # Handle message only if server still running
                if self._running:
                    # Use same socket to respond to new peer
                    self._handle_client(self._sock, addr, msg)
        except socket.error as err:
            self._logger.fatal('Receive loop failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)

    def _handle_client(self, sock: socket.socket, addr: Tuple[str, int], data: bytes):
        self._logger.info('Receive data from {0}:{1}.'.format(addr[0], str(addr[1])))
        # Send to all other clients new client
        for client in self.clients:
            self._send_msg(self._sock, pickle.dumps(addr), client)

        # Keep track of new client
        if addr not in self.clients:
            # Send public address to client and store it
            for client in self.clients:
                self._send_msg(self._sock, pickle.dumps(client), addr)
            self.clients.append(addr)
            # Welcome new client
            self._send_msg(self._sock, b'Welcome !', addr)

    def _data_loop(self) -> None:
        """Wait for data to be sent. Should run on a separated thread."""
        self._logger.debug('Waiting for messages to be sent.')
        with socket.socket(self._socketFamily, self._socketType, socket.IPPROTO_UDP) as s:
            s.bind(('', 0))
            while self._running:
                # Reduce CPU overhead
                time.sleep(1 / 100.0)
                # Check container
                if (not self._container.empty()):
                    msg, addr = self._container.get(block=True)
                    self._send_msg(s, msg, addr)

    def _send_msg(self, sock: socket.socket, msg: Any, addr: Tuple[str, int]) -> None:
        # @TODO Sent information should be different based on message received
        template = 'Send message to {0}:{1} using interface {2}:{3}.'
        if (isinstance(msg, str)):
            sock.sendto(msg.encode(self._encoding), addr)
        else:
            sock.sendto(msg, addr)
        self._logger.info(template.format(addr[0], addr[1],
                                          *sock.getsockname()))

    def _bind(self) -> None:
        self._sock.bind((self._host, self._port))
        self._logger.debug('Socket binded (host = {0}) with port {1}.'.format(self._host, self._port))
        print("Rendez-vous Server Up and running on {0}:{1}".format(self._host, self._port))

    def _stop(self) -> None:
        """
            Contact himself to unlock `func::_receive_loop` blocking call and go out of infinite loop
            without errors.
        """
        # Safe as assignment is atomic
        self._running = False
        # Fake message to break infinite loop waiting for a message (see _receive_loop)
        with socket.socket(self._socketFamily, self._socketType, socket.IPPROTO_UDP) as s:
            if (self._host in ('0.0.0.0', '')):
                self._send_msg(s, '__AskClose__', ('localhost', self._port))
            else:
                self._send_msg(s, '__AskClose__', (self._host, self._port))

    def _reset(self) -> None:
        self._receiveThread = None
        self._dataThread = None
        self.clients = list()

    def __del__(self):
        """Needed in case user forgets to call stop explicitly."""
        if (self._running):
            self._logger.warning('Close server before garbage collection.')
            self.stop()


if __name__ == '__main__':
    # LOG
    # LOG = 'RendezVous'
    from logger import add_stream_handler, add_file_handler
    # Minimal level for logs
    log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)
    file_handler = add_file_handler('RendezVous.log', parent='RendezVous',
                                    level=log_level, filemode='a')
    stream_handler = add_stream_handler(parent='RendezVous', level=log_level)

    # SERVER
    server = RendezVousServerUDP()
    server.start('0.0.0.0', 5000)
    # Stay up x seconds
    time.sleep(100)
    # Stop server
    server.stop()
