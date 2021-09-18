__all__ = ['BoneMarketArgumentParser']
__author__ = "Jeremy Saklad"

from argparse import ArgumentParser

class BoneMarketArgumentParser(ArgumentParser):
    """An ArgumentParser with the ability to read files with any number of space-delimited arguments on a line."""

    __slots__ = 'description', 'argument_default', 'prefix_chars', 'conflict_handler', 'prog', 'usage', 'epilog', 'formatter_class', 'fromfile_prefix_chars', 'add_help', 'allow_abbrev', 'exit_on_error'

    def convert_arg_line_to_args(self, arg_line):
        return arg_line.split()
