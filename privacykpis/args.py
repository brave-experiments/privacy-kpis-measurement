import argparse


class Args:
    def __init__(self, args: argparse.Namespace):
        self.is_valid = False
        self.debug = args.debug

    def valid(self):
        return self.is_valid
