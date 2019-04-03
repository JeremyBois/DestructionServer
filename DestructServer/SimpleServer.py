# -*- coding:Utf8 -*-

"""
    Multi threaded TCP server.
      - One thread to handle client connection
      - Two thread for each new client
        - Listening thread
        - Sending thread
"""

import logging
import socket
import threading

from typing import List, Any
Threads = List[threading.Thread]


class DestructServer(object):

    """
    Multi threaded TCP server.
      - One thread to handle client connection
      - Two thread for each new client
        - Listening thread
        - Sending thread
    """

    def __init__(self, host: str, port: int):
        super().__init__()

        # Assign logger
        self.logging = logging.getLogger(__name__)

        # Store global data
        self._running = False
        self._port = port
        self._host = host

        # Init TCP socket
        self._socketFamily = socket.AF_INET
        self._socketType = socket.SOCK_STREAM
        self._sock = socket.socket(self._socketFamily, self._socketType)
        # Force reuse of a port
        # self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Keep track of thread
        self._acceptThread = None    # type: Any
        self._listeningThreads = []  # type: Threads
        self._sendingThreads = []    # type: Threads
        self._registerLock = threading.Lock()
        self._count = 0
        self._nameT = '{0}-{2}::{1}'

    def Start(self) -> bool:
        """Start TCP server."""
        try:
            self._Bind()
            self._Listen()

            # Start thread to handle client connection
            self._acceptThread = threading.Thread(target=self._StartServer,
                                                  name='AcceptThread')
            self._acceptThread.start()

        except socket.error as err:
            self._sock.close()
            self.logging.fatal('Start failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)
            self.logging.debug('Socket now closed (port {0}).'.format(self._port))
            return False
        return True

    def Stop(self) -> bool:
        """Stop TCP server."""
        if not self._running:
            self.logging.info('DestructServer is not running')
            return True

        actionResult = False

        try:
            self._StopAccept()
            # Wait for accept thread that wait for client threads...
            self._acceptThread.join()
            # Clean
            self._Reset()
            actionResult = True
        except socket.error as err:
            self.logging.fatal('Stop failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)
            actionResult = False
        finally:
            self._sock.close()
            self.logging.debug('Server socket now closed (port {0}).'.format(self._port))

        return actionResult

    def _StartServer(self):
        """Wrapper around Accept server loop. Should be running on a separated thread."""
        try:
            self._running = True
            self._AcceptLoop()

            # Wait for client threads
            for listenThread, sendThread in zip(self._listeningThreads, self._sendingThreads):
                listenThread.join()
                sendThread.join()
        except socket.error as err:
            self.logging.fatal('Accept loop failed due to (code {0}) --> {1}'.format(err.args[0], str(err)), exc_info=True)

    def _Bind(self):
        self._sock.bind((self._host, self._port))
        self.logging.debug('Socket binded (host = {0}) with port {1}.'.format(self._host, self._port))

    def _Listen(self):
        self.logging.info('DestructServer started.')
        # Now listening
        self._sock.listen()
        self.logging.debug('Socket now listening to port {0}.'.format(self._port))

    def _AcceptLoop(self):
        while self._running:
            self.logging.info('Waiting for connections.')
            # Wait for connection
            newClient, addr = self._sock.accept()

            # Start in another thread only if we are still listening
            if self._running:
                with self._registerLock:
                    self.logging.info('Connection with {0}:{1} succeeded.'.format(addr[0], str(addr[1])))

                    # Start threads
                    self._listeningThreads.append(threading.Thread(target=self._ListenClient,
                                                                   args=(newClient, addr),
                                                                   name=self._nameT.format('Receive', addr[0], self._count)))
                    self._listeningThreads[-1].start()
                    self._sendingThreads.append(threading.Thread(target=self._SendClient,
                                                                 args=(newClient, addr),
                                                                 name=self._nameT.format('Send', addr[0], self._count)))
                    self._sendingThreads[-1].start()

                self._count += 1

    def _ListenClient(self, client: socket.socket, addr: tuple):
        self.logging.debug('Starting Listen thread for {0}:{1}.'.format(addr[0], str(addr[1])))

    def _SendClient(self, client: socket.socket, addr: tuple):
        self.logging.debug('Starting Send thread for {0}:{1}.'.format(addr[0], str(addr[1])))

    def _StopAccept(self):
        """Connect to yourself to unlock `func::_AcceptLoop` blocking call to go out of infinite loop without errors"""
        # Safe as assignment is atomic
        self._running = False
        # Temporary socket to fake a connection
        with socket.socket(self._socketFamily, self._socketType) as s:
            s.connect(('localhost', self._port))

    def _Reset(self):
        self._acceptThread = None
        self._listeningThreads = []
        self._sendingThreads = []
