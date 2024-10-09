"""
This file provides the basic functions to perform asynchronous tasks.
It provides the 3 functions:
 * ensure_future(coroutine): schedules the task described by the coroutine and
                             returns a Future that can be used as argument of
                             the following functions:
 * sleep(time_s): blocks the commandline for time_s, without blocking other
                  tasks such as gui update...
 * wait(future, timeout=None): blocks the commandline until future is set or
                               timeout expires.

BEWARE: sleep() and wait() can be used behind a qt slot (for instance in
response to a QPushButton being pressed), however, they will fail if used
inside a coroutine. In this case, one should use the builtin await (in
place of wait) and the asynchronous sleep coroutine provided below (in
place of sleep):
  * async_sleep(time_s): await this coroutine to stall the execution for a
                         time time_s within a coroutine.

These functions are provided in place of the native asyncio functions in
order to integrate properly within the IPython (Jupyter) Kernel. For this,
Main loop of the application:
In an Ipython (Jupyter) notebook with qt integration:
    %gui qt
     fut = ensure_future(some_coroutine(), loop=LOOP) # executes anyway in
the background loop
#    LOOP.run_until_complete(fut) # only returns when fut is ready
# BEWARE ! inside some_coroutine, calls to asyncio.sleep_async() have to be
# made this way:
#    asyncio.sleep(sleep_time, loop=LOOP)
# Consequently, there is a coroutine async_utils.async_sleep(time_s)
# Finally this file provide a sleep() function that waits for the execution of
# sleep_async and that should be used in place of time.sleep.

"""
import logging
from qtpy import QtCore, QtWidgets
import asyncio
from asyncio import Future, iscoroutine, TimeoutError, get_event_loop, wait_for
import sys
import nest_asyncio
import qasync

logger = logging.getLogger(name=__name__)

# enable ipython QtGui support if needed
try:
    from IPython import get_ipython
    IPYTHON = get_ipython()
    IPYTHON.run_line_magic("gui", "qt")
except BaseException as e:
    logger.debug('Could not enable IPython gui support: %s.' % e)

APP = QtWidgets.QApplication.instance()
if APP is None:
    # logger.debug('Creating new QApplication instance "pyrpl"')
    APP = QtWidgets.QApplication(['pyrpl'])


LOOP = None  # the main event loop
INTERACTIVE = True  # True if we are in an interactive IPython session

try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell':
        msg = 'async_utils: Jupyter notebook or qtconsole'
    elif shell == 'TerminalInteractiveShell':
        LOOP = qasync.QEventLoop(already_running=False)
        INTERACTIVE = False
        msg = 'async_utils: Terminal running IPython'
    else:
        LOOP = qasync.QEventLoop(already_running=False)
        INTERACTIVE = False
        msg = 'async_utils: # Other type (?)'
        asyncio.events._set_running_loop(LOOP)
except NameError:
    LOOP = qasync.QEventLoop(already_running=False)
    INTERACTIVE = False
    msg = 'async_utils: Probably standard Python interpreter'
    asyncio.events._set_running_loop(LOOP)

logger.debug(msg)
if INTERACTIVE:
    nest_asyncio.apply()

async def sleep_async(time_s):
    """
    Replaces asyncio.sleep(time_s) inside coroutines. Deals properly with
    IPython kernel integration.
    """
    await asyncio.sleep(time_s)

def ensure_future(coroutine):
    """
    Schedules the task described by the coroutine. Deals properly with
    IPython kernel integration.
    """
    if INTERACTIVE:
        return asyncio.ensure_future(coroutine)
    else:
        return asyncio.ensure_future(coroutine, loop=LOOP)

def wait(future, timeout=None):
    """
    This function is used to turn async coroutines into blocking functions:
    Returns the result of the future only once it is ready. This function
    won't block the eventloop while waiting for other events.
    ex:
    def curve(self):
        curve = scope.curve_async()
        return wait(curve)

    BEWARE: never use wait in a coroutine (use builtin await instead)
    """
    new_future = ensure_future(asyncio.wait({future},
                                            timeout=timeout))

    if INTERACTIVE:
        new_future = wait_for(future, timeout)
        loop = get_event_loop()
        try:
            return loop.run_until_complete(new_future)
        except TimeoutError:
            logger.error('async_utils wait: Timout exceeded')
    else:
        LOOP.run_until_complete(new_future)
        done, pending = new_future.result()
        if future in done:
            return future.result()
        else:
            msg = 'async_utils wait: Timout exceeded'
            logger.error(msg)
            raise TimeoutError("Timout exceeded")


def sleep(time_s):
    """
    Blocks the commandline for time_s. This function doesn't block the
    eventloop while executing.
    BEWARE: never sleep in a coroutine (use await sleep_async(time_s) instead)
    """
    wait(ensure_future(sleep_async(time_s)))


class Event(asyncio.Event):
    """
    Use this Event instead of asyncio.Event() to signal an event. This
    version deals properly with IPython kernel integration.
    Example: Resuming scope acquisition after a pause (acquisition_module.py)
        def pause(self):
            if self._running_state=='single_async':
                self._running_state=='paused_single'
            _resume_event = Event()

        async def _single_async(self):
            for self.current_avg in range(1, self.trace_average):
                if self._running_state=='paused_single':
                    await self._resume_event.wait()
            self.data_avg = (self.data_avg * (self.current_avg-1) + \
                             await self._trace_async(0)) / self.current_avg

    """

    def __init__(self):
        super(Event, self).__init__()
