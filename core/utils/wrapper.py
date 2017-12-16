# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: wrapper.py
#     date: 2017-12-07
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
#  IMPORTS
# =============================================================================
from functools import wraps
from utils.logging import get_logger
# =============================================================================
#  GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  FUNCTIONS
# =============================================================================


def lazy_getter(cls_member_name):
    # -------------------------------------------------------------------------
    # lazy_getter
    # -------------------------------------------------------------------------
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwds):
            if not hasattr(self, cls_member_name):
                setattr(self, cls_member_name, f(self, *args, **kwds))

            return getattr(self, cls_member_name)

        return wrapped

    return wrapper


def __in(called, *args, **kwds):
    # -------------------------------------------------------------------------
    # __in
    # -------------------------------------------------------------------------
    LGR.debug("I> {}(...)".format(called))


def __out(called, ret):
    # -------------------------------------------------------------------------
    # __out
    # -------------------------------------------------------------------------
    LGR.debug("O> {}(...) => ...".format(called))


def trace():
    # -------------------------------------------------------------------------
    # trace
    # -------------------------------------------------------------------------
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwds):
            cls_name = type(self).__name__
            method_name = f.__name__
            called = "{}.{}".format(cls_name, method_name)
            __in(called, args, kwds)

            ret = f(self, *args, **kwds)

            __out(called, ret)
            return ret

        return wrapped

    return wrapper


def trace_static(cls_name):
    # -------------------------------------------------------------------------
    # trace_static
    # -------------------------------------------------------------------------
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwds):
            called = "{}.{}".format(cls_name, f.__name__)
            __in(called, args, kwds)

            ret = f(*args, **kwds)

            __out(called, ret)
            return ret

        return wrapped

    return wrapper


def trace_func(module_name):
    # -------------------------------------------------------------------------
    # trace_func
    # -------------------------------------------------------------------------
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwds):
            called = "{}.{}".format(module_name, f.__name__)
            __in(called, args, kwds)

            ret = f(*args, **kwds)

            __out(called, ret)
            return ret

        return wrapped

    return wrapper
