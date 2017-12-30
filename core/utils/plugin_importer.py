# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: plugin_importer.py
#     date: 2017-12-13
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
import os
import importlib as implib
import utils.config as config
from utils.logging import get_logger
from utils.wrapper import trace
from utils.exceptions import PluginImportException
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for plugin importer.
##
class PluginImporter(object):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      import_root     The import root
    ## @param      caller          The caller
    ## @param      subdir          The subdir
    ## @param      recursive       The recursive
    ## @param      expected_funcs  The expected funcs
    ##
    def __init__(self, import_root, caller, subdir, recursive=True,
                 expected_funcs=set()):
        super(PluginImporter, self).__init__()
        self.skip_failing_import = config.value('skip_failing_import', False)
        self.expected_funcs = expected_funcs
        self.import_root = import_root
        self.search_root = os.path.join(os.path.dirname(caller), subdir)
        self.recursive = recursive
        self.plugins = {}
        self.valid = None
    ##
    ## @brief      { function_description }
    ##
    ## @param      error  The error
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __import_failure(self, error):
        self.valid = False
        LGR.error(error)
        if not self.skip_failing_import:
            raise PluginImportException(error)
    ##
    ## @brief      { function_description }
    ##
    ## @param      plugin       The plugin
    ## @param      plugin_name  The plugin name
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __register_plugin(self, plugin, plugin_name):
        plugin_funcs = set(dir(plugin))
        missing_funcs = plugin_funcs.intersection(self.expected_funcs)
        missing_funcs = missing_funcs.symmetric_difference(self.expected_funcs)
        missing_funcs = list(missing_funcs)

        if len(missing_funcs) > 0:
            error = "failed to add:\n"
            error += "\t{}\n".format(dissector)
            error += "\t>>> details: missing mandatory functions"
            error += " ({}).".format(missing_funcs)
            return error

        self.plugins[plugin_name] = plugin
        LGR.info("plugin <{}> registered.".format(plugin_name))

        return None
    ##
    ## @brief      Loads plugins.
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def load_plugins(self):
        self.valid = True

        LGR.info("loading plugins from <{}>".format(self.search_root))
        for root, dirs, files in os.walk(self.search_root):

            if not self.recursive:
                dirs[:] = []

            relroot = root.replace(self.search_root, '').split(os.sep)
            relroot = list(filter(None, relroot))

            for f in files:
                if f.endswith('.py'):

                    plugin = f[:-3]
                    if '.' in plugin:
                        self.__import_failure("plugin name contains at least "
                                              "one dot...")

                    import_parts = [self.import_root] + relroot + [plugin]
                    import_path = '.'.join(import_parts)

                    try:
                        imported_plugin = implib.import_module(import_path)
                        imported_plugin.name = plugin
                    except Exception as e:
                        error = "failed to import <{}>".format(import_path)
                        LGR.exception(error)
                        self.__import_failure(error)

                    error = self.__register_plugin(imported_plugin, plugin)
                    if error is not None:
                        self.__import_failure(error)

        return self.valid
