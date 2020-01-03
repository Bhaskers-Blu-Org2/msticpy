# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Module for magic classes."""
from typing import Any, Mapping, Union

from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import line_cell_magic, Magics, magics_class

import pandas as pd

from ..sectools import base64unpack as base64
from ..sectools.iocextract import IoCExtract
from .._version import VERSION

__version__ = VERSION
__author__ = "Ian Hellen"


@magics_class
class IoCExtractMagic(Magics):
    def __init__(self, shell):
        # You must call the parent constructor
        super().__init__(shell)
        self._ioc_extract = IoCExtract()

    @line_cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        "--verbose", "-v", action="store_true", help="Whether to print the results"
    )
    def ioc(self, line="", cell=None):
        if cell is None:
            results = self._ioc_extract.extract(src=line)
            print(results)
            return line
        else:
            results = self._ioc_extract.extract(src=cell)
            return line, cell
        print("hello " + cell)


ip = get_ipython()
ip.register_magics(IoCExtractMagic)


try:
    from bs4 import BeautifulSoup

    _bs_print = True
except ImportError:
    _bs_print = False


@magics_class
class Base64Magic(Magics):
    @line_cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        "--out", "-o", help="The variable to return the results in"
    )
    @magic_arguments.argument(
        "--pretty", "-p", help="Print formatted version of output", action="store_true"
    )
    def b64(self, line="", cell=None):
        if cell is None:
            results, df_results = base64.unpack(line)

        else:
            results, df_results = base64.unpack(cell)
        if _bs_print:
            xml_str = f"<decoded_string>{results}</decoded_string>"
            bs = BeautifulSoup(xml_str, "xml")
            results = bs.prettify()
        args = magic_arguments.parse_argstring(self.b64, line)
        if args.out is not None:
            self.shell.user_ns[args.out] = (results, df_results)
        if args.pretty is not None:
            print(results)
        return results


ip = get_ipython()
ip.register_magics(Base64Magic)


@pd.api.extensions.register_dataframe_accessor("ioc")
class IoCExtractAccessor:
    def __init__(self, pandas_obj):
        self._df = pandas_obj
        self._ioc = IoCExtract()

    def extract(self, cols, **kwargs):
        return self._ioc.extract_df(data=self._df, columns=cols, **kwargs)


@pd.api.extensions.register_dataframe_accessor("b64")
class B64ExtractAccessor:
    def __init__(self, pandas_obj):
        self._df = pandas_obj

    def extract(self, col, **kwargs):
        return base64.unpack_df(data=self._df, column=col, **kwargs)
