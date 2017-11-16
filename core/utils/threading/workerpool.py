#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: workerpool.py
#    date: 2017-11-12
#  author: paul.dautry
# purpose:
#   
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 paul.dautry
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
import multiprocessing as mp
#===============================================================================
# FUNCTIONS
#===============================================================================
def dissect(container, dissectors):
    for dissector in dissectors:
        if dissector.can_dissect(container):
            dissector.dissect(container)

def worker_routine(queue, dissectors):
    while True:
        container = queue.get()
        # if next container is None it means EXIT NOW
        if container is None:
            break
        # foreach new container resulting of the dissection, add it to the 
        # dissect queue
        for new_container in dissect(container, dissectors):
            queue.put(new_container)
        queue.task_done()
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# WorkerPool
#-------------------------------------------------------------------------------
class WorkerPool(object):
    def __init__(self, num_workers, dissectors):
        super(WorkerPool, self).__init__()
        self.num_workers = num_workers
        self.dissectors = dissectors
        self.workers = []
        self.queue = mp.Queue()
    #---------------------------------------------------------------------------
    # process
    #---------------------------------------------------------------------------
    def process(self, containers):
        # add given containers to lifo
        for container in containers:
            self.queue.put(container)
        # create as much workers as needed
        for i in range(self.num_workers):
            worker = mp.Process(
                target=worker_routine, 
                args=(self.queue, self.dissectors))
            worker.start()
            self.workers.append(worker)
        # wait for the lifo to be empty
        self.queue.join()
        # stop all workers
        for i in range(self.num_workers):
            self.queue.put(None)
        for worker in self.workers:
            worker.join()
