import os
import logging

from Project.server import create_app
from Project.tools.logger import add_file_handler, add_stream_handler

from werkzeug.serving import is_running_from_reloader

from dotenv import load_dotenv


if __name__ == "__main__":
    # Load environment variables
    load_dotenv(verbose=True, dotenv_path='.env')

    # Minimal level for logs
    log_level = logging.DEBUG

    # Keep stream handler for Werkzeug
    logging.getLogger().setLevel(log_level)

    # Init logging for UDP / TCP server
    file_handler = add_file_handler('DestruckServer.log', parent='DestruckServer',
                                    level=log_level, filemode='a')
    stream_handler = add_stream_handler(parent='DestruckServer', level=log_level)

    # Only stream my logs but store https server logs (werkzeug)
    logging.getLogger('werkzeug').addHandler(file_handler)

    # Python anywhere import create_app from wsgi
    app, socketio, udpServer = create_app('dev')

    # Also add handler to Flask's logger for cases where Werkzeug isn't used as the underlying WSGI server.
    app.logger.addHandler(file_handler)

    port = int(os.environ.get('PORT', 5000))

    # Wrap with socketIO
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

    # Closing gracefully UDP server
    if (not is_running_from_reloader()):
        udpServer.stop()
