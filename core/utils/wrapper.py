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
    """
    @brief      Wraps a class method with this function to turn it into a lazy
                getter.
                Class member value will be computed on the first call to this
                function and will never be computed again after that.

    @param      cls_member_name  Name of the member to use

    @return     wrapper
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwds):
            if not hasattr(self, cls_member_name):
                setattr(self, cls_member_name, f(self, *args, **kwds))

            return getattr(self, cls_member_name)

        return wrapped

    return wrapper


def __in(called, *args, **kwds):
    """
    @brief      Traces when a function is entered

    @param      called  Called function's complete name
    @param      args    Arguments passed to the function
    @param      kwds    Keyword args passed to the function
    """
    LGR.debug("I> {}(...)".format(called))


def __out(called, ret):
    """
    @brief      Traces when a function is left

    @param      called  Called function's complete name
    @param      ret     Called function's return value
    """
    LGR.debug("O> {}(...) => ...".format(called))


def trace():
    """
    @brief      Wraps a method with this function to trace when it's called

    @return     wrapper
    """
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
    """
    @brief      Wraps a static method with this function to trace when it's
                called

    @param      cls_name  Class' name

    @return     wrapper
    """
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
    """
    @brief      Wraps a module function with this function to trace when it's
                called

    @param      module_name  The module name

    @return     wrapper
    """
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
