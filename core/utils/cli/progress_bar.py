# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: progress_bar.py
#     date: 2017-12-19
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
from utils.cli.backspace_printer import BackspacePrinter
# =============================================================================
#  CLASSES
# =============================================================================
##
## @brief      Class for progress bar.
##             Example :
##             ```
##             import time
##             from utils.cli import CLIProgressBar
##
##             if __name__ == '__main__':
##                 bar = CLIProgressBar(show_exact=True)
##                 total = 100
##                 bar.init(total)
##                 for i in range(total):
##                     j = i+1
##                     bar.update(j, 'even' if (j % 2 == 0) else 'odd')
##                     time.sleep(0.5)
##                 bar.done()
##             ```
##
class ProgressBar(BackspacePrinter):
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      show_percentage  The show percentage
    ## @param      show_exact       The show exact
    ## @param      bar_chars        The bar characters
    ##
    def __init__(self, show_percentage=True, show_exact=False,
                 bar_chars=('[', '>', '=', ']')):
        if len(bar_chars) != 4:
            raise ValueError("bar_chars is expected to be a 4 chars tuple")

        super(CLIProgressBar, self).__init__()
        self.show_percentage = show_percentage
        self.show_exact = show_exact
        self.total = 100.0
        self.begin = bar_chars[0]
        self.halfcell = bar_chars[1]
        self.fullcell = bar_chars[2]
        self.end = bar_chars[3]
        self.prev_bar = ""
    ##
    ## @brief      { function_description }
    ##
    ## @param      value  The value
    ##
    ## @return     { description_of_the_return_value }
    ##
    def __floatify(self, value):
        if isinstance(value, int):
            return float(value)

        return value
    ##
    ## @brief      { function_description }
    ##
    ## @param      total  The total
    ##
    ## @return     { description_of_the_return_value }
    ##
    def init(self, total):
        total = self.__floatify(total)

        if not isinstance(total, float) or total < 0.0:
            raise ValueError("total must be in [0.0, +inf[")

        self.total = total
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      value  The value
    ## @param      text   The text
    ##
    ## @return     { description_of_the_return_value }
    ##
    def update(self, value, text=''):
        value = self.__floatify(value)
        if not isinstance(value, float) or value < 0.0 or value > self.total:
            raise ValueError("value must be a float in [0.0, "
                             "{}]".format(self.total))

        perc = (value / self.total) * 100

        percentage = ""
        if self.show_percentage:
            percentage = " {:5.1f}%".format(perc)

        exact = ""
        if self.show_exact:
            exact = " {:.1f}/{:.1f}".format(value, self.total)

        q = int(perc) // 2
        r = int(perc) % 2

        bar = "{}{}{}{}{}".format(self.begin,
                                  self.fullcell * q,
                                  self.halfcell * r,
                                  RePrinter.BLANK * (50 - (q + r)),
                                  self.end)

        self.prev_bar = "{}{}{} {}".format(bar, percentage, exact, text)
        self.print(self.prev_bar)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    def done(self):
        self.total = 100.0
        self.finish(self.prev_bar)
