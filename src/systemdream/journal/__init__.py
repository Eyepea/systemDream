#  -*- Mode: python; coding:utf-8; indent-tabs-mode: nil -*- */
#
#  This file come from systemd.
#
#  Copyright 2012 David Strauss <david@davidstrauss.net>
#  Copyright 2012 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
#  Copyright 2012 Marti Raudsepp <marti@juffo.org>
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
#  systemd is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with systemd; If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import sys as _sys
import datetime as _datetime
import uuid as _uuid
import traceback as _traceback
import os as _os
import logging as _logging
if _sys.version_info >= (3,3):
    from collections import ChainMap as _ChainMap
from syslog import (LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR,
                    LOG_WARNING, LOG_NOTICE, LOG_INFO, LOG_DEBUG)
# from ._journal import __version__, sendv, stream_fd
# from ._reader import (_Reader, NOP, APPEND, INVALIDATE,
#                       LOCAL_ONLY, RUNTIME_ONLY,
#                       SYSTEM, SYSTEM_ONLY, CURRENT_USER,
#                       _get_catalog)
# from . import id128 as _id128
#

from .helpers import send
