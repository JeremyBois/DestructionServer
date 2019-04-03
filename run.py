# -*- coding:Utf8 -*-

import logging

from DestructServer.SimpleServer import DestructServer
from DestructServer.Tools import log_basicConfig, add_stream_handler

import time


# Start the development server using the run() method
if __name__ == "__main__":
    # Global variables for server
    LOG_LEVEL = logging.DEBUG
    PORT = 51515
    HOST = '0.0.0.0'
    LOG_NAME = 'DestructionServer.log'

    # Setup logging
    fmt = '%(asctime)s %(levelname)-9s: %(threadName)-16s|| %(name)-35s %(funcName)-25s >> %(message)s'
    log_basicConfig(LOG_NAME, LOG_LEVEL, filemode='a', fmt=fmt)
    fmt = '%(levelname)-9s: %(threadName)-16s|| %(name)-35s %(funcName)-25s >> %(message)s'
    add_stream_handler(LOG_LEVEL, fmt=fmt)

    # Start server destruction
    logging.debug('Server will start shortly.')
    app = DestructServer(HOST, PORT)
    app.Start()

    # Wait for testing only
    time.sleep(20)
    app.Stop()
