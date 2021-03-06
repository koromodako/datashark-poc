# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: workerpool.py
#    date: 2017-11-12
#  author: koromodako
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 koromodako
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import multiprocessing as mp
import utils.crypto as crypto
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_func
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================

@trace_func(__name__)
def worker_routine(iqueue, oqueue, routine, kwargs):
    """
    @brief      This generic routine implements a specific producer-consumer
                relation as the consumer here can also be a producer.

    @param      iqueue   Input queue shared between workers
    @param      oqueue   Output queue collecting workers' results
    @param      routine  Routine used to process input queue tasks
    @param      kwargs   Keyword arguments to be passed to the routine
    """
    # re-init crypto context after worker fork
    crypto.re_init()
    # enter worker infinite loop
    while True:
        # take next available task
        LGR.debug('retrieving task...')
        task = iqueue.get()
        # if next task is None it means EXIT NOW
        if task is None:
            LGR.debug('process exiting!')
            iqueue.task_done()  # validate None task
            break
        # perform routine on task
        LGR.debug('calling routine...')
        try:
            (iq, oq) = routine(task, **kwargs)
        except Exception as e:
            LGR.exception("a worker caught an internal exception; details "
                          "below:")
        else:
            # re-inject results if needed
            for e in iq:
                iqueue.put(e)
            for e in oq:
                oqueue.put(e)
        finally:
            # task has been processed
            iqueue.task_done()
        LGR.debug('task done.')
# =============================================================================
# CLASSES
# =============================================================================


class WorkerPool(object):
    """
    @brief      Creates a pool of workers able to process tasks in parallel
                until input task queue is empty.
    """
    def __init__(self, num_workers):
        """
        @brief      Constructor

        @param      num_workers Number of workers to spawn
        """
        super(WorkerPool, self).__init__()
        self.num_workers = num_workers
        self.workers = []
        self.iqueue = mp.JoinableQueue()
        self.oqueue = mp.Queue()

    @trace()
    def map(self, routine, kwargs, tasks):
        """
        @brief      Maps tasks to be processed by routine on underlying workers

        @param      routine Routine to be mapped on multiple workers.
        @param      kwargs  Keyword arguments to be passed to the routine.
                            Keep in mind that these arguments will be shared
                            between workers.
        @param      tasks   Tasks to be processed by workers using routine

        @return     processing results
        """
        # add tasks to fifo
        LGR.debug('adding tasks to input queue...')
        for task in tasks:
            self.iqueue.put(task)
        # create as much workers as needed
        LGR.debug('creating {} workers...'.format(self.num_workers))
        for i in range(self.num_workers):
            worker = mp.Process(
                target=worker_routine,
                args=(self.iqueue, self.oqueue, routine, kwargs))
            worker.start()
            self.workers.append(worker)
        # wait for the fifo to be empty
        LGR.debug('waiting for iqueue to be empty...')
        self.iqueue.join()
        # stop all workers
        LGR.debug('stoping processes...')
        for i in range(self.num_workers):
            self.iqueue.put(None)
        # fill results array
        LGR.debug('consume results...')
        results = []
        while not self.oqueue.empty():
            results.append(self.oqueue.get())
        # wait for all workers to terminate
        for i in range(len(self.workers)):
            LGR.debug('waiting worker n°{} to terminate...'.format(i))
            self.workers[i].join()
        self.workers = []
        # finally returns all results
        return results
