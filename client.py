import logging
from datetime import datetime, timezone  # Requires Python 3.2

from s3rat import S3Comm


log = logging.getLogger(__name__ if __name__ != '__main__' else 'client')


if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser(description="Send commands to S3 for server to execute")
    cli.add_argument('bucket', help="S3 Bucket name to use")
    cli.add_argument('session', help="Session ID")
    cli.add_argument('command', nargs='*', help="Single command to send")
    args = cli.parse_args()
    print("Starting S3RAT client...")
    comm = S3Comm(args.bucket)
    sid = comm.start_session(args.session)
    print("Found Session ID:", sid)
    comm.wait_for("0_server_ready.txt")
    print("Server is ready")
    if len(args.command) > 0:
        timestamp = datetime.now(timezone.utc).strftime("%H%M%SZ")
        comm.upload("{}.cmd".format(timestamp), " ".join(args.command))
        print("Sent Command:", " ".join(args.command))
        comm.wait_for("{}.result".format(timestamp))
        result = comm.download("{}.result".format(timestamp))
        print(result)
