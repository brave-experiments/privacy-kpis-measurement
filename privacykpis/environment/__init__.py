import argparse

import privacykpis.args
import privacykpis.browsers
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

        # These are only used for MacOS
        self.proxy_port = str(args.proxy_port)
        self.proxy_host = args.proxy_host

        self.is_valid = True


def configure(args: Args) -> None:
    case_module = privacykpis.browsers.browser_class(args)
    if args.install:
        case_module.setup_env(args)
    else:  # uninstall path.
        case_module.teardown_env(args)
