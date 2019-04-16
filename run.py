import os
import logging

from Project.server import create_app
from Project.tools.logger import add_file_handler

from dotenv import load_dotenv


if __name__ == "__main__":
    # Load environment variables
    load_dotenv(verbose=True, dotenv_path='.env')

    # Minimal level for logs
    log_level = logging.DEBUG

    # Keep stream handler for Werkzeug
    logging.getLogger().setLevel(log_level)

    # Init logging for server
    api_handler = add_file_handler('dev_api_log.log', parent='werkzeug', level=log_level)
    logging.getLogger('DestructServer').addHandler(api_handler)

    # Python anywhere import create_app from wsgi
    app, socketio = create_app('dev')

    # Also add handler to Flask's logger for cases where Werkzeug isn't used as the underlying WSGI server.
    app.logger.addHandler(api_handler)

    port = int(os.environ.get('PORT', 5000))

    # Wrap with socketIO
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
