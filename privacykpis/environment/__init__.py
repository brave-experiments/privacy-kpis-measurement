import argparse

import privacykpis.args
import privacykpis.common


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        if not args.install and not args.uninstall:
            privacykpis.common.err("Must select 'install' or 'uninstall'")
            return

        if args.install and args.uninstall:
            privacykpis.common.err("Cannot both 'install' and 'uninstall'")
            return

        if not privacykpis.common.is_root():
            privacykpis.common.err("you'll need to run as root to configure "
                                   "the environment")
            return

        self.uninstall = args.uninstall
        self.install = args.install
        self.case = args.case
        self.is_valid = True


def configure(args: Args):
    case_module = privacykpis.common.module_for_args(args)
    if args.install:
        case_module.setup_env(args)
    else:  # uninstall path.
        case_module.teardown_env(args)
