from __future__ import division
import os
import socket

import sys as _sys
import datetime as _datetime
import uuid as _uuid


UNIX_SOCKET = '/run/systemd/journal/socket'
_JOURNALD_SOCKET = None

# if _sys.version_info >= (3,):
#     from ._reader import Monotonic
# else:
Monotonic = tuple


def _convert_monotonic(m):
    return Monotonic((_datetime.timedelta(microseconds=m[0]),
                      _uuid.UUID(bytes=m[1])))

def _convert_source_monotonic(s):
    return _datetime.timedelta(microseconds=int(s))

def _convert_realtime(t):
    return _datetime.datetime.fromtimestamp(t / 1000000)

def _convert_timestamp(s):
    return _datetime.datetime.fromtimestamp(int(s) / 1000000)

def _convert_trivial(x):
    return x

if _sys.version_info >= (3,):
    def _convert_uuid(s):
        return _uuid.UUID(s.decode())
else:
    _convert_uuid = _uuid.UUID

DEFAULT_CONVERTERS = {
    'MESSAGE_ID': _convert_uuid,
    '_MACHINE_ID': _convert_uuid,
    '_BOOT_ID': _convert_uuid,
    'PRIORITY': int,
    'LEADER': int,
    'SESSION_ID': int,
    'USERSPACE_USEC': int,
    'INITRD_USEC': int,
    'KERNEL_USEC': int,
    '_UID': int,
    '_GID': int,
    '_PID': int,
    'SYSLOG_FACILITY': int,
    'SYSLOG_PID': int,
    '_AUDIT_SESSION': int,
    '_AUDIT_LOGINUID': int,
    '_SYSTEMD_SESSION': int,
    '_SYSTEMD_OWNER_UID': int,
    'CODE_LINE': int,
    'ERRNO': int,
    'EXIT_STATUS': int,
    '_SOURCE_REALTIME_TIMESTAMP': _convert_timestamp,
    '__REALTIME_TIMESTAMP': _convert_realtime,
    '_SOURCE_MONOTONIC_TIMESTAMP': _convert_source_monotonic,
    '__MONOTONIC_TIMESTAMP': _convert_monotonic,
    '__CURSOR': _convert_trivial,
    'COREDUMP': bytes,
    'COREDUMP_PID': int,
    'COREDUMP_UID': int,
    'COREDUMP_GID': int,
    'COREDUMP_SESSION': int,
    'COREDUMP_SIGNAL': int,
    'COREDUMP_TIMESTAMP': _convert_timestamp,
    }

_IDENT_LETTER = set('ABCDEFGHIJKLMNOPQRTSUVWXYZ_')

def _valid_field_name(s):
    return not (set(s) - _IDENT_LETTER)

# @todo: Reimplement _get_catalog function
# def get_catalog(mid):
#     if isinstance(mid, _uuid.UUID):
#         mid = mid.hex
#     return _get_catalog(mid)

def _make_line(field, value):
    if isinstance(value, bytes):
        return field.encode('utf-8') + b'=' + value
    elif isinstance(value, int):
        return field + '=' + str(value)
    else:
        return field + '=' + value

def sendv(*args):
    global _JOURNALD_SOCKET
    if not os.path.exists(UNIX_SOCKET):
        raise ValueError('This system doesn\'t have journald')

    if not _JOURNALD_SOCKET:
        _JOURNALD_SOCKET = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        _JOURNALD_SOCKET.connect(UNIX_SOCKET)
    packet = ('\n'.join(args)+'\n').encode('utf-8')
    _JOURNALD_SOCKET.sendall(packet)