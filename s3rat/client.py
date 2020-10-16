from __future__ import print_function
import logging
import sys
from datetime import datetime

from . import UTC, get_result_name, S3Comm


log = logging.getLogger(__name__ if __name__ != '__main__' else 'client')

if sys.version_info.major == 2:
    input = raw_input


def cli_setup_parser(subparser):
    cli = subparser.add_parser('client', description="Send commands to S3 for server to execute")
    cli.add_argument('bucket', help="S3 Bucket name to use")
    cli.add_argument('session', help="Session ID")
    group = cli.add_mutually_exclusive_group()
    group.add_argument('--command', nargs='+', help="Single command to send")
    group.add_argument('--file', type=open, help="Script to send ('.py' or '.sh')")
    cli.set_defaults(func=cli_main)


def cli_main(args):
    print("Starting S3RAT client...")
    comm = S3Comm(args.bucket)
    sid = comm.start_session(args.session)
    print("Found Session ID:", sid)
    server_id = comm.download("0_server_identity.json")
    print("Server Info:")
    print(server_id)
    if 'command' in args and args.command:
        timestamp = datetime.now(UTC).strftime("%H%M%SZ")
        comm.upload("{}.cmd".format(timestamp), " ".join(args.command))
        print("Sent Command:", " ".join(args.command))
        result_name = get_result_name("{}.cmd".format(timestamp))
        comm.wait_for(result_name)
        print(comm.download(result_name))
    elif 'file' in args and args.file:
        timestamp = datetime.now(UTC).strftime("%H%M%SZ")
        comm.upload("{}_{}".format(timestamp, args.file.name), args.file.read())
        print("Sent Script:", "{}_{}".format(timestamp, args.file.name))
        result_name = get_result_name("{}_{}".format(timestamp, args.file.name))
        comm.wait_for(result_name)
        print(comm.download(result_name))
    else:  # If no command and no file, start interactive command mode
        print("Entering interactive mode... (type 'exit' to end)")
        while True:
            timestamp = datetime.now(UTC).strftime("%H%M%SZ")
            try:
                cmd = input('{} > '.format(timestamp))
                if cmd == "exit":
                    break  # break loop on exit
                if cmd.strip() == "":
                    continue  # re-prompt if no input
                comm.upload("{}.cmd".format(timestamp), cmd)
                result_name = get_result_name("{}.cmd".format(timestamp))
                comm.wait_for(result_name)
                print(comm.download(result_name))
            except EOFError:
                break
            except KeyboardInterrupt:
                break
        print(" -- End -- ")
