import logging
import random
import string
import hashlib
from base64 import b64encode
from datetime import datetime, timezone  # Requires Python 3.2
import boto3
from botocore.exceptions import WaiterError


log = logging.getLogger(__name__ if __name__ != '__main__' else 'comms')


class S3Comm(object):
    """ The S3 communication session """

    last_check = None
    known_objects = list()
    uploaded_objects = list()

    def __init__(self, bucket, prefix=None, **kwargs):
        """
        Setup the communication session

        :param bucket: S3 bucket to use
        :param prefix: S3 key prefix to add (additional prefix is added with date, time, session_id)
        :param session_id: added at the end of the prefix or randomly generated if not provided
        :param kwargs: additional arguments to pass to boto3.session.Session.client (like "region_name")
        """
        self.bucket = bucket
        self.created = datetime.now(timezone.utc)
        path_list = []
        if prefix:
            path_list.append(prefix)
        path_list.extend([str(self.created.year), str(self.created.month), str(self.created.day)])
        self.day_prefix = "/".join(path_list)
        self.prefix = None  # Session Prefix
        self.client = boto3.client('s3', **kwargs)

    def start_session(self, session_id=None):
        """ Start a new session or configure for an existing session

        If provided, search for session_id to add to today's prefix.  Otherwise, create a new session prefix.

        :param session_id: unique ID of session to establish
        :return: session_id
        """
        session_name = None
        if session_id:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=(self.day_prefix + '/'), Delimiter='/')
            for p in response.get('CommonPrefixes', []):
                if p['Prefix'].endswith(session_id + '/'):
                    session_name = p['Prefix'][len(self.day_prefix) + 1:-1]
            if not session_name:
                raise ValueError("Session ID '{}' Not Found".format(session_id))
        else:
            session_id = ''.join([random.choice(string.ascii_letters+string.digits) for _ in range(8)])
            session_name = "{}_{}".format(self.created.strftime("%H%M%SZ"), session_id)
        self.prefix = "/".join([self.day_prefix, session_name])
        log.info("Setup S3Comm with bucket='%s', prefix='%s' (kwargs: %s)",
                 self.bucket, self.prefix)
        return session_id

    def wait_for(self, name, delay=5, max_attempts=20):
        """ Wait for object to exist or raise TimeoutError if failed

        :param name: name of file in session to wait for
        :param delay: seconds between poll attempts
        :param max_attempts: attempts before error
        """
        waiter = self.client.get_waiter('object_exists')
        log.info("Wait for Object: %s", name)
        try:
            waiter.wait(Bucket=self.bucket, Key="/".join([self.prefix, name]),
                        WaiterConfig={'Delay': delay, 'MaxAttempts': max_attempts})
        except WaiterError:
            raise TimeoutError("Waiting for Object '{}'".format(name))

    def check(self):
        """ Checks for any new files within session

        :return: list of new files, not yet processed
        """
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=self.prefix)
        if response['IsTruncated']:
            log.warning("S3Comms.check:S3.ListObjectsV2 response is truncated!")
        new_objects = list()
        prefix_len = len(self.prefix) + 1
        for obj in response.get('Contents', []):
            obj_name = obj['Key'][prefix_len:]
            if obj_name not in self.uploaded_objects and obj_name not in self.known_objects:
                log.info("Found new object: %s", obj_name)
                new_objects.append(obj_name)
            else:
                log.info("Object is not new: %s", obj_name)
        self.last_check = datetime.strptime(response['ResponseMetadata']["HTTPHeaders"]["date"],
                                            "%a, %d %b %Y %H:%M:%S %Z")
        return new_objects

    def download(self, name):
        """ Download data from object in S3

        :param name: name to download
        :return: object body as text (str)
        """
        log.info("Download Object: %s", name)
        obj_data = self.client.get_object(Bucket=self.bucket, Key="/".join([self.prefix, name]))
        return obj_data['Body'].read().decode('utf-8')

    def upload(self, name, body):
        """ Upload data as a file in the current session.

        :param name: filename to use when uploading (str)
        :param body: data to upload (str)
        :return:
        """
        put_obj_args = {
            "ACL": "bucket-owner-full-control",
            "Bucket": self.bucket,
            "Key": "/".join([self.prefix, name]),
            "Body": body.encode('utf-8'),
            "ContentType": "text/plain;charset=UTF-8"
        }
        if 'md5' in hashlib.algorithms_available:
            h = hashlib.md5()
            h.update(body.encode('utf-8'))
            put_obj_args['ContentMD5'] = b64encode(h.digest()).decode('utf-8')
        else:
            log.warning("S3 Upload without ContentMD5 checksum")
        log.info("Upload Object: %s", name)
        self.client.put_object(**put_obj_args)
        self.uploaded_objects.append(name)

    def remember(self, name):
        """ Add to the list of known objects to prevent returning it with the next check

        :param name: name as would be returned by self.check (requires 'Key', 'LastModified', and 'ETag')
        """
        self.known_objects.append(name)
