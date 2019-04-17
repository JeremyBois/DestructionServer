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

from queue import Queue

# Static typing checking
from typing import Tuple

from Project.server import LOG


__all__ = ['RendezVousServerUDP']


class RendezVousServerUDP(object):

    """
    Multi threaded UDP server.
      - One thread to handle clients messages
      - A new thread created after each client connection
    """

    def __init__(self, encoding: str = 'utf-8'):
        """
            Select host and port used to communicate with the server.
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
        self._sock = socket.socket(self._socketFamily, self._socketType)
        # Force reuse of a port
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Keep track of thread
        self._receiveThread = None     # type: Any
        self._sendThread = None        # type: Any

        # Data
        self._recvContainer = Queue()  # Queue[str, str]

    def start(self, host: str, port: int) -> bool:
        """Start UDP server."""
        try:
            # Update port used
            self._port = port
            self._host = host
            self._bind()

            # Start thread to handle clients incoming messages
            self._receiveThread = threading.Thread(target=self._receive_loop,
                                                   name='Receive')
            self._receiveThread.start()

            # Start thread to send response back to clients
            self._sendThread = threading.Thread(target=self._send_loop,
                                                name='Send')
            self._sendThread.start()

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
            self._receiveThread.join()
            self._sendThread.join()
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
                self._logger.info('Waiting for connections.')
                # Wait for message (max size of 4096)
                msg, addr = self._sock.recvfrom(4096)

                # Handle message only if server still running
                if self._running:
                    self._logger.info('Receive data from {0}:{1}.'.format(addr[0], str(addr[1])))
                    # Store message to handle it later
                    self._recvContainer.put((msg, addr), block=True)
        except socket.error as err:
            self._logger.fatal('Receive loop failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)

    def _send_loop(self) -> None:
        """Wait for messages to be sent. Should run on a separated thread."""
        # @TODO use event loop instead of while loop
        self._logger.debug('Waiting for messages to be sent.')
        with socket.socket(self._socketFamily, self._socketType) as s:
            while self._running:
                # Sleep
                time.sleep(1 / 100)
                # Check container
                if (not self._recvContainer.empty()):
                    msg, addr = self._recvContainer.get(block=True)
                    self._send_msg(s, 'Welcome to the server dear client...\n', addr)

    def _send_msg(self, sock: socket.socket, msg: str, addr: Tuple[str, str]) -> None:
        # @TODO Sent information should be different based on message received
        sock.sendto(msg.encode(self._encoding), addr)

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
        with socket.socket(self._socketFamily, self._socketType) as s:
            self._send_msg(s, '__AskClose__', (self._host, self._port))

    def _reset(self) -> None:
        self._receiveThread = None
        self._sendThread = None

    def __del__(self):
        """Needed in case user forgets to call stop explicitly."""
        if (self._running):
            self._logger.info('Close server before garbage collection.')
            self.stop()


if __name__ == '__main__':
    server = RendezVousServerUDP()
    server.start('localhost', 5000)
    time.sleep(10)
    server.stop()
