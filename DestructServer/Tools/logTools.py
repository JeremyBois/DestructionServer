#! /usr/bin/env python
# -*- coding:Utf8 -*-


"""
    Some helper function to control logging module interaction without
    knowledge of :class:`logging`.
"""


import logging


__all__ = ['add_file_handler', 'add_stream_handler', 'log_basicConfig']


def add_file_handler(filename, level=logging.DEBUG, filemode='w',
                     parent=None, fmt=None, datefmt=None):
    """Add a logger which will write to *filename* events according to
    logging level and *filemode*.

    :param filename: Path of the file used for logging message.
    :param level: Minimal logging level to write to *filename*
                  (default to logging.DEBUG)
    :param filemode: Mode used to control the file
                     (default to 'w')
    :param parent: Select where to attach the new file handler.
                   :data:`None` means to root logger (default).
    :param fmt: Format used for message
                (default to '%(asctime)s %(levelname)-8s: %(name)-35s %(funcName)-25s >> %(message)s')
    :param datefmt: Format used for datetime
                    (default '%Y-%m-%d %H:%M:%S')
    """
    fmt = fmt if fmt is not None else '%(asctime)s %(levelname)-8s: %(name)-35s %(funcName)-25s >> %(message)s'
    datefmt = datefmt if datefmt is not None else '%Y-%m-%d %H:%M:%S'
    file_handler = logging.FileHandler(filename,
                                       filemode, encoding="utf-8")
    file_handler.setLevel(level)
    formatter = logging.Formatter(fmt=fmt,
                                  datefmt=datefmt)
    file_handler.setFormatter(formatter)
    # Add the handler to parent (None return root logger)
    logging.getLogger(parent).addHandler(file_handler)


def add_stream_handler(level=logging.INFO,
                       parent=None, fmt=None, datefmt=None):
    """Add a logger which will write to **stdout** events according to
    logging level.

    :param level: Minimal logging level to write to *filename*
                  (default to logging.DEBUG)
    :param parent: Select where to attach the new file handler.
                   :data:`None` means to root logger (default).
    :param fmt: Format used for message
                (default to '%(levelname)-8s: %(name)-35s %(funcName)-25s >> %(message)s')
    :param datefmt: Format used for datetime
                    (default '%Y-%m-%d %H:%M:%S')
    """
    fmt = fmt if fmt is not None else '%(levelname)-8s: %(name)-35s %(funcName)-25s >> %(message)s'
    datefmt = datefmt if datefmt is not None else '%Y-%m-%d %H:%M:%S'

    cons_handler = logging.StreamHandler()
    cons_handler.setLevel(level)
    formatter = logging.Formatter(fmt=fmt,
                                  datefmt=datefmt)
    cons_handler.setFormatter(formatter)
    logging.getLogger(parent).addHandler(cons_handler)


def log_basicConfig(filename='log.log', level=logging.DEBUG, filemode='a',
                    fmt=None, datefmt=None):
    """Configure logging root basic behavior. Handlers attach to

    :param filename: Path of the file used for logging message
                     (default to 'log.log')
    :param level: Minimal logging level to write to *filename*
                  (default to logging.DEBUG)
    :param filemode: Mode used to control the file
                     (default to 'a')
    :param fmt: Format used for message
                (default to '%(asctime)s %(levelname)-8s: %(name)-35s %(funcName)-25s >> %(message)s')
    :param datefmt: Format used for datetime
                    (default '%Y-%m-%d %H:%M:%S')

    .. note::
        Default configuration creates a *filename* 'log.log' where main script
        is running. Each new lauch of the script is concatenate to *filename*.
        That is, the log is never removed, new logs are added.

    .. seealso::
        :meth:`logging.basicConfig` and :class:`logging` documentation if
        more control needed over logging initialization.

    """
    fmt = fmt if fmt is not None else '%(asctime)s %(levelname)-8s: %(name)-35s %(funcName)-25s >> %(message)s'
    datefmt = datefmt if datefmt is not None else '%Y-%m-%d %H:%M:%S'
    # Configure root logger with default behavior
    logging.basicConfig(level=level,
                        format=fmt,
                        datefmt=datefmt,
                        filename=filename,
                        filemode=filemode)
