import argparse
import logging

from . import log, client, server


if __name__ == '__main__':
    cli = argparse.ArgumentParser(prog='s3rat', description="S3 Remote Access Tool")
    cli.add_argument('--debug', action='store_true', help="activate debug messages")
    subcmds = cli.add_subparsers(title="mode", description="(select operation mode and add -h for more help)",
                                 help="operation mode")
    subcmds.required = True  # See Bug:  http://bugs.python.org/issue9253#msg186387
    subcmds.dest = 'mode'
    client.cli_setup_parser(subcmds)
    server.cli_setup_parser(subcmds)
    args = cli.parse_args()
    if args.debug:
        logging.basicConfig()
        log.setLevel(logging.DEBUG)
    args.func(args)
