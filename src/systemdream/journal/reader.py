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

# @todo: Direct import from python-systemd, it doesn't work yet, pull requests welcome

class Reader(_Reader):
    """Reader allows the access and filtering of systemd journal
    entries. Note that in order to access the system journal, a
    non-root user must be in the `systemd-journal` group.

    Example usage to print out all informational or higher level
    messages for systemd-udevd for this boot:

    >>> j = journal.Reader()
    >>> j.this_boot()
    >>> j.log_level(journal.LOG_INFO)
    >>> j.add_match(_SYSTEMD_UNIT="systemd-udevd.service")
    >>> for entry in j:
    ...    print(entry['MESSAGE'])

    See systemd.journal-fields(7) for more info on typical fields
    found in the journal.
    """
    def __init__(self, flags=0, path=None, files=None, converters=None):
        """Create an instance of Reader, which allows filtering and
        return of journal entries.

        Argument `flags` sets open flags of the journal, which can be one
        of, or ORed combination of constants: LOCAL_ONLY (default) opens
        journal on local machine only; RUNTIME_ONLY opens only
        volatile journal files; and SYSTEM_ONLY opens only
        journal files of system services and the kernel.

        Argument `path` is the directory of journal files. Note that
        `flags` and `path` are exclusive.

        Argument `converters` is a dictionary which updates the
        DEFAULT_CONVERTERS to convert journal field values. Field
        names are used as keys into this dictionary. The values must
        be single argument functions, which take a `bytes` object and
        return a converted value. When there's no entry for a field
        name, then the default UTF-8 decoding will be attempted. If
        the conversion fails with a ValueError, unconverted bytes
        object will be returned. (Note that ValueEror is a superclass
        of UnicodeDecodeError).

        Reader implements the context manager protocol: the journal
        will be closed when exiting the block.
        """
        super(Reader, self).__init__(flags, path, files)
        if _sys.version_info >= (3,3):
            self.converters = _ChainMap()
            if converters is not None:
                self.converters.maps.append(converters)
            self.converters.maps.append(DEFAULT_CONVERTERS)
        else:
            self.converters = DEFAULT_CONVERTERS.copy()
            if converters is not None:
                self.converters.update(converters)

    def _convert_field(self, key, value):
        """Convert value using self.converters[key]

        If `key` is not present in self.converters, a standard unicode
        decoding will be attempted.  If the conversion (either
        key-specific or the default one) fails with a ValueError, the
        original bytes object will be returned.
        """
        convert = self.converters.get(key, bytes.decode)
        try:
            return convert(value)
        except ValueError:
            # Leave in default bytes
            return value

    def _convert_entry(self, entry):
        """Convert entire journal entry utilising _covert_field"""
        result = {}
        for key, value in entry.items():
            if isinstance(value, list):
                result[key] = [self._convert_field(key, val) for val in value]
            else:
                result[key] = self._convert_field(key, value)
        return result

    def __iter__(self):
        """Part of iterator protocol.
        Returns self.
        """
        return self

    def __next__(self):
        """Part of iterator protocol.
        Returns self.get_next() or raises StopIteration.
        """
        ans = self.get_next()
        if ans:
            return ans
        else:
            raise StopIteration()

    if _sys.version_info < (3,):
        next = __next__

    def add_match(self, *args, **kwargs):
        """Add one or more matches to the filter journal log entries.
        All matches of different field are combined in a logical AND,
        and matches of the same field are automatically combined in a
        logical OR.
        Matches can be passed as strings of form "FIELD=value", or
        keyword arguments FIELD="value".
        """
        args = list(args)
        args.extend(_make_line(key, val) for key, val in kwargs.items())
        for arg in args:
            super(Reader, self).add_match(arg)

    def get_next(self, skip=1):
        """Return the next log entry as a mapping type, currently
        a standard dictionary of fields.

        Optional skip value will return the `skip`\-th log entry.

        Entries will be processed with converters specified during
        Reader creation.
        """
        if super(Reader, self)._next(skip):
            entry = super(Reader, self)._get_all()
            if entry:
                entry['__REALTIME_TIMESTAMP'] =  self._get_realtime()
                entry['__MONOTONIC_TIMESTAMP']  = self._get_monotonic()
                entry['__CURSOR']  = self._get_cursor()
                return self._convert_entry(entry)
        return dict()

    def get_previous(self, skip=1):
        """Return the previous log entry as a mapping type,
        currently a standard dictionary of fields.

        Optional skip value will return the -`skip`\-th log entry.

        Entries will be processed with converters specified during
        Reader creation.

        Equivalent to get_next(-skip).
        """
        return self.get_next(-skip)

    def query_unique(self, field):
        """Return unique values appearing in the journal for given `field`.

        Note this does not respect any journal matches.

        Entries will be processed with converters specified during
        Reader creation.
        """
        return set(self._convert_field(field, value)
                   for value in super(Reader, self).query_unique(field))

    def wait(self, timeout=None):
        """Wait for a change in the journal. `timeout` is the maximum
        time in seconds to wait, or None, to wait forever.

        Returns one of NOP (no change), APPEND (new entries have been
        added to the end of the journal), or INVALIDATE (journal files
        have been added or removed).
        """
        us = -1 if timeout is None else int(timeout * 1000000)
        return super(Reader, self).wait(us)

    def seek_realtime(self, realtime):
        """Seek to a matching journal entry nearest to `realtime` time.

        Argument `realtime` must be either an integer unix timestamp
        or datetime.datetime instance.
        """
        if isinstance(realtime, _datetime.datetime):
            realtime = float(realtime.strftime("%s.%f")) * 1000000
        return super(Reader, self).seek_realtime(int(realtime))

    def seek_monotonic(self, monotonic, bootid=None):
        """Seek to a matching journal entry nearest to `monotonic` time.

        Argument `monotonic` is a timestamp from boot in either
        seconds or a datetime.timedelta instance. Argument `bootid`
        is a string or UUID representing which boot the monotonic time
        is reference to. Defaults to current bootid.
        """
        if isinstance(monotonic, _datetime.timedelta):
            monotonic = monotonic.totalseconds()
        monotonic = int(monotonic * 1000000)
        if isinstance(bootid, _uuid.UUID):
            bootid = bootid.hex
        return super(Reader, self).seek_monotonic(monotonic, bootid)

    def log_level(self, level):
        """Set maximum log `level` by setting matches for PRIORITY.
        """
        if 0 <= level <= 7:
            for i in range(level+1):
                self.add_match(PRIORITY="%d" % i)
        else:
            raise ValueError("Log level must be 0 <= level <= 7")

    def messageid_match(self, messageid):
        """Add match for log entries with specified `messageid`.

        `messageid` can be string of hexadicimal digits or a UUID
        instance. Standard message IDs can be found in systemd.id128.

        Equivalent to add_match(MESSAGE_ID=`messageid`).
        """
        if isinstance(messageid, _uuid.UUID):
            messageid = messageid.hex
        self.add_match(MESSAGE_ID=messageid)

    def this_boot(self, bootid=None):
        """Add match for _BOOT_ID equal to current boot ID or the specified boot ID.

        If specified, bootid should be either a UUID or a 32 digit hex number.

        Equivalent to add_match(_BOOT_ID='bootid').
        """
        if bootid is None:
            bootid = _id128.get_boot().hex
        else:
            bootid = getattr(bootid, 'hex', bootid)
        self.add_match(_BOOT_ID=bootid)

    def this_machine(self, machineid=None):
        """Add match for _MACHINE_ID equal to the ID of this machine.

        If specified, machineid should be either a UUID or a 32 digit hex number.

        Equivalent to add_match(_MACHINE_ID='machineid').
        """
        if machineid is None:
            machineid = _id128.get_machine().hex
        else:
            machineid = getattr(machineid, 'hex', machineid)
        self.add_match(_MACHINE_ID=machineid)