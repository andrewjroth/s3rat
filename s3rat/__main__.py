import argparse

from . import client, server


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description="S3 Remote Access Tool")
    subcmds = cli.add_subparsers(title="mode", help="select operation mode (add -h for more help)")
    client.cli_setup_parser(subcmds)
    server.cli_setup_parser(subcmds)
    args = cli.parse_args()
    args.func(args)
