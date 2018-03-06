import botocore.auth
import os
import re

from datetime import timedelta


# Get libfaketime settings from the environment variables.

if 'libfaketime.so.1' in os.environ.get('LD_PRELOAD', ''):
    FAKETIME_STRING = os.environ.get('FAKETIME')
    if FAKETIME_STRING:
        FAKETIME_FILE = None
    else:
        FAKETIME_FILE = os.environ.get('FAKETIME_TIMESTAMP_FILE')
        if not FAKETIME_FILE:
            if os.path.exists(os.path.expanduser('~/.faketimerc')):
                FAKETIME_FILE = os.path.expanduser('~/.faketimerc')
            elif os.path.exists('/etc/faketimerc'):
                FAKETIME_FILE = '/etc/faketimerc'
            else:
                raise RuntimeError(
                    'could not determine libfaketime environment settings'
                )
else:
    FAKETIME_STRING = None
    FAKETIME_FILE = None

# Support offset strings according to https://github.com/wolfcw/libfaketime
# Relative date offsets can be positive or negative, thus what you put into
# FAKETIME _must_ either start with a + or a -, followed by a number, and
# optionally followed by a multiplier.

FAKETIME_OFFSET_RE = re.compile('([+-])(\d+)([mhdy])?')


def get_faketime_timedelta():
    """
    Returns a time delta object that represents the configured libfaketime
    offset. If libfaketime is configured differently, e.g. with absolute
    values, then this function will raise an exception.

    """

    if FAKETIME_STRING:
        offset_string = FAKETIME_STRING
    else:
        with open(FAKETIME_FILE) as faketime_file:
            offset_string = faketime_file.read().strip()

    match = FAKETIME_OFFSET_RE.match(offset_string)

    if not match:
        raise ValueError(
            'Required relative offset, found: {}'.format(offset_string)
        )

    sign = match.group(1)
    number = int(match.group(2))
    unit = match.group(3)

    if sign == '-':
        number *= -1

    if unit is None:
        return timedelta(seconds=number)
    elif unit == 'm':
        return timedelta(minutes=number)
    elif unit == 'h':
        return timedelta(hours=number)
    elif unit == 'd':
        return timedelta(days=number)
    elif unit == 'y':
        return timedelta(years=number)
    else:
        raise ValueError('Unknown libfaketime time unit: {}'.format(unit))


def undo_faketime_timedelta(method):
    """
    Wraps a class method to undo the effects of a libfaketime relative offset.

    """

    @classmethod
    def wrapper(cls, *args, **kwargs):
        faketime_offset = get_faketime_timedelta()
        faketime_affected_value = method(*args, **kwargs)
        return faketime_affected_value - faketime_offset

    return wrapper


class PatchedDatetimeModule(object):
    """
    Wrapper for the datetime module that reverses libfaketime relative offsets
    when calling datetime.date.today(), datetime.datetime.now(), and
    datetime.datetime.utcnow().

    """

    def __init__(self, datetime):

        self._datetime = datetime

        class date(datetime.date):
            today = undo_faketime_timedelta(datetime.date.today)

        class datetime(datetime.datetime):
            now = undo_faketime_timedelta(datetime.datetime.now)
            utcnow = undo_faketime_timedelta(datetime.datetime.utcnow)

        self.date = date
        self.datetime = datetime

    def __getattr__(self, name):
        return getattr(self._datetime, name)


def patch_botocore():
    """
    Patches botocore to work while using libfaketime relative offsets.

    """

    if FAKETIME_STRING or FAKETIME_FILE:

        botocore.auth.datetime = PatchedDatetimeModule(
            datetime=botocore.auth.datetime,
        )

        # It looks like requests made using some older AWS signature versions
        # would require patching the following variables, but I'm not sure
        # how to test them.
        # * botocore.auth.formatdate for email.formatdate(usegmt=True)
        # * botocore.auth.time for time.gmtime() and time.time()
