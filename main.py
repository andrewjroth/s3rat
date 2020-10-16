import argparse

import s3rat


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description="S3 Remote Access Tool")
    subcmds = cli.add_subparsers(title="mode")
    s3rat.client.cli_setup_parser(subcmds)
    s3rat.server.cli_setup_parser(subcmds)
    args = cli.parse_args()
    args.func(args)
