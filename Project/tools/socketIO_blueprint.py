# Project/tools/socketIO_blueprint.py


class IOBlueprint:

    def __init__(self, namespace='/', **kwargs):
        self.namespace = namespace
        self._handlers = []

    def on(self, key):
        """ A decorator to add a handler to a blueprint."""
        def wrapper(wrappedFunc):
            if not callable(wrappedFunc):
                raise ValueError('Handle must wrap a callable')

            def wrap(io):
                @io.on(key, namespace=self.namespace)
                def wrapped(*args, **kwargs):
                    return wrappedFunc(*args, **kwargs)
                return io
            self._handlers.append(wrap)
        return wrapper

    def init_io(self, io):
        for handler in self._handlers:
            handler(io)
        return io
