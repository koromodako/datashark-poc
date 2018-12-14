# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: db_adapter.py
#     date: 2017-12-20
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 koromodako
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
import multiprocessing as mp
from utils.wrapper import trace
from utils.logging import get_logger
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Abstract representation of a DB adapter plugin.
##
class DBAdapter(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      conf  The conf
    ##
    def __init__(self, conf):
        super(DBAdapter, self).__init__()
        ## @brief Configuration of the adapter
        self._conf = conf
        ## @brief Multiprocessing lock to prevent concurrency issues
        self._lock = mp.Lock()
        ## @brief Open mode can be 'r' or 'w'
        self.__mode = None
        ## @brief Is self a valid instance ?
        self.__valid = False
    ##
    ## @brief      Checks if configuration is valid. Subclasses must implement
    ##             this method
    ##
    ## @return     True if self._conf is valid, False otherwise.
    ##
    def _check_conf(self):
        raise NotImplementedError
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _init_r(self):
        raise NotImplementedError
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _init_w(self):
        raise NotImplementedError
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _term_r(self):
        raise NotImplementedError
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def _term_w(self):
        raise NotImplementedError
    ##
    ## @brief      Returns expected configuration as a ConfigObj
    ##
    ## @return     Must return a ConfigObj instance
    ##
    @trace()
    def expected_conf(self):
        #return ConfigObj({})
        raise NotImplementedError
    ##
    ## @brief      { function_description }
    ##
    ## @param      mode  The mode
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def init(self, mode):
        if mode not in ['r', 'w']:
            raise ValueError("mode must be one of ['r', 'w']")
        self.__mode = mode

        if not self._check_conf():
            self.__valid = False
            return

        if self.__mode == 'r':
            self.__valid = self._init_r()
        else:
            self.__valid = self._init_w()
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def term(self):
        if self.__mode == 'r':
            self._term_r()
        else:
            self._term_w()
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self.__valid

