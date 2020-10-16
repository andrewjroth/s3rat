# s3RAT -- Remote Access Tool using S3

This tool is designed to use S3 as a transfer point for sending commands and 
getting results from a remote server.  The client and the server must both have
access to the same S3 bucket.

S3 is used as a transfer point because it can commonly be used in areas where
network access is limited, such as within a private VPC.

This is a work in progress.

## Quick Start

This package will work with Python 2.7 or Python 3.  Python 2.7 support was 
added because it remains the default for most systems, including Amazon Linux.

Package requires boto3, which might be installed from a system package.
Install using one of the commands below.

```shell
yum install python27-boto3  # Python 2.7 on Amazon Linux
yum install python2-boto3   # Python 2.7 on Amaxon Linux 2
pip install boto3  # Any system with pip
```

AWS credentials must be configured per the AWS CLI and/or Python SDK for AWS.

For details on how to run the tool, run the module from the command line.

```shell
python -m s3rat -h
```
