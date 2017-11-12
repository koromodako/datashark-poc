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
from threading import Thread
#===============================================================================
# CLASSES
#===============================================================================
class WorkerPool(object):
    def __init__(self, max_workers):
        super(WorkerPool, self).__init__()
        self.max_workers = max_workers
        self.workers = []

    def results(self):
        results = []
        to_remove = []
        for worker in self.workers:
            if not worker.is_alive():
                to_remove.append(worker)
        for worker in to_remove:
            worker.join()
            results.append(worker.result)
            self.workers.remove(worker)
        return results

    def exec_task(func, args):
        if len(self.workers) < self.max_workers:
            worker = Worker(target=func, args=args)
            worker.start()
            self.workers.append(worker)
            return True
        return False

