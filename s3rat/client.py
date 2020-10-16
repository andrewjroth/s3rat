import logging
from datetime import datetime, timezone  # Requires Python 3.2

from . import get_result_name, S3Comm


log = logging.getLogger(__name__ if __name__ != '__main__' else 'client')


def cli_setup_parser(subparser):
    cli = subparser.add_parser('client', description="Send commands to S3 for server to execute")
    cli.add_argument('bucket', help="S3 Bucket name to use")
    cli.add_argument('session', help="Session ID")
    group = cli.add_mutually_exclusive_group(required=True)
    group.add_argument('--command', nargs='+', help="Single command to send")
    group.add_argument('--file', type=open, help="Script to send ('.py' or '.sh')")
    cli.set_defaults(func=cli_main)


def cli_main(args):
    print("Starting S3RAT client...")
    comm = S3Comm(args.bucket)
    sid = comm.start_session(args.session)
    print("Found Session ID:", sid)
    comm.wait_for("0_server_ready.txt")
    print("Server is ready")
    timestamp = datetime.now(timezone.utc).strftime("%H%M%SZ")
    if 'command' in args and args.command:
        comm.upload("{}.cmd".format(timestamp), " ".join(args.command))
        print("Sent Command:", " ".join(args.command))
        result_name = get_result_name("{}.cmd".format(timestamp))
        comm.wait_for(result_name)
        print(comm.download(result_name))
    elif 'file' in args:
        comm.upload("{}_{}".format(timestamp, args.file.name), args.file.read())
        print("Sent Script:", "{}_{}".format(timestamp, args.file.name))
        result_name = get_result_name("{}_{}".format(timestamp, args.file.name))
        comm.wait_for(result_name)
        print(comm.download(result_name))
    else:
        pass  # TODO: Create interactive session
