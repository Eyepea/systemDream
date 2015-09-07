from __future__ import division
import os
import socket

import sys as _sys
import logging as _logging
from syslog import (LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR,
                    LOG_WARNING, LOG_NOTICE, LOG_INFO, LOG_DEBUG)
import collections
from .helpers import send
from .utils import _valid_field_name

DEFAULT_SOCKET = 'unix:/run/systemd/journal/socket'


def _make_socket(sendto_socket):
    if sendto_socket.startswith('unix:'):
        sock_type, socket_address = sendto_socket.split(':', 1)
        if not os.path.exists(socket_address):
            raise ValueError('This system doesn\'t have journald')

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.connect(socket_address)

    elif sendto_socket.startswith('udp:'):
        sock_type, socket_address = sendto_socket.split(':', 1)
        host, port = socket_address.split(':', 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((host, int(port)))

    else:
        if sendto_socket.startswith('tcp:'):
            sock_type, socket_address = sendto_socket.split(':', 1)
        else:
            socket_address = sendto_socket

        # tcp address with no port is a bad address, something must be wrong here...
        if ':' not in sendto_socket:
            raise ValueError('Invalid url: %s' % sendto_socket)

        host, port = socket_address.split(':', 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, int(port)))

    return sock


class JournalHandler(_logging.Handler):
    """Journal handler class for the Python logging framework.

    Please see the Python logging module documentation for an
    overview: http://docs.python.org/library/logging.html.

    To create a custom logger whose messages go only to journal:

    >>> log = logging.getLogger('custom_logger_name')
    >>> log.propagate = False
    >>> log.addHandler(journal.JournalHandler())
    >>> log.warn("Some message: %s", detail)

    Note that by default, message levels `INFO` and `DEBUG` are
    ignored by the logging framework. To enable those log levels:

    >>> log.setLevel(logging.DEBUG)

    To redirect all logging messages to journal regardless of where
    they come from, attach it to the root logger:

    >>> logging.root.addHandler(journal.JournalHandler())

    For more complex configurations when using `dictConfig` or
    `fileConfig`, specify `systemd.journal.JournalHandler` as the
    handler class.  Only standard handler configuration options
    are supported: `level`, `formatter`, `filters`.

    To attach journal MESSAGE_ID, an extra field is supported:

    >>> import uuid
    >>> mid = uuid.UUID('0123456789ABCDEF0123456789ABCDEF')
    >>> log.warn("Message with ID", extra={'MESSAGE_ID': mid})

    Fields to be attached to all messages sent through this
    handler can be specified as keyword arguments. This probably
    makes sense only for SYSLOG_IDENTIFIER and similar fields
    which are constant for the whole program:

    >>> journal.JournalHandler(SYSLOG_IDENTIFIER='my-cool-app')

    The following journal fields will be sent:
    `MESSAGE`, `PRIORITY`, `THREAD_NAME`, `CODE_FILE`, `CODE_LINE`,
    `CODE_FUNC`, `LOGGER` (name as supplied to getLogger call),
    `MESSAGE_ID` (optional, see above), `SYSLOG_IDENTIFIER` (defaults
    to sys.argv[0]).
    """

    def __init__(self, level=_logging.NOTSET, sendto_socket=DEFAULT_SOCKET, **kwargs):
        super(JournalHandler, self).__init__(level)

        self.socket = _make_socket(sendto_socket)

        for name in kwargs:
            if not _valid_field_name(name):
                raise ValueError('Invalid field name: ' + name)
        if 'SYSLOG_IDENTIFIER' not in kwargs:
            kwargs['SYSLOG_IDENTIFIER'] = _sys.argv[0]
        self.sendto_socket = sendto_socket
        self._extra = kwargs

    def emit(self, record):
        """Write record as journal event.

        MESSAGE is taken from the message provided by the
        user, and PRIORITY, LOGGER, THREAD_NAME,
        CODE_{FILE,LINE,FUNC} fields are appended
        automatically. In addition, record.MESSAGE_ID will be
        used if present.
        """
        if record.args and isinstance(record.args, collections.Mapping):
            extra = dict(self._extra, **record.args)  # Merge metadata from handler and record
        else:
            extra = self._extra
        try:
            msg = self.format(record)
            pri = self.mapPriority(record.levelno)
            mid = getattr(record, 'MESSAGE_ID', None)
            send(msg,
                 SOCKET=self.socket,
                 MESSAGE_ID=mid,
                 PRIORITY=format(pri),
                 LOGGER=record.name,
                 THREAD_NAME=record.threadName,
                 CODE_FILE=record.pathname,
                 CODE_LINE=record.lineno,
                 CODE_FUNC=record.funcName,
                 **extra)
        except Exception:
            self.handleError(record)

    @staticmethod
    def mapPriority(levelno):
        """Map logging levels to journald priorities.

        Since Python log level numbers are "sparse", we have
        to map numbers in between the standard levels too.
        """
        if levelno <= _logging.DEBUG:
            return LOG_DEBUG
        elif levelno <= _logging.INFO:
            return LOG_INFO
        elif levelno <= _logging.WARNING:
            return LOG_WARNING
        elif levelno <= _logging.ERROR:
            return LOG_ERR
        elif levelno <= _logging.CRITICAL:
            return LOG_CRIT
        else:
            return LOG_ALERT
