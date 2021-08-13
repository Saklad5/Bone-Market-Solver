__all__ = ['BoneMarketArgumentParser']
__author__ = "Jeremy Saklad"

from argparse import ArgumentParser

class BoneMarketArgumentParser(ArgumentParser):
    """An ArgumentParser with the ability to read files with any number of space-delimited arguments on a line."""
    def convert_arg_line_to_args(self, arg_line):
        return arg_line.split()
