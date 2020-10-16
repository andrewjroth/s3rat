# s3RAT -- Remote Access Tool using S3

This tool is designed to use S3 as a transfer point for sending commands and 
getting results from a remote server.  The client and the server must both have
access to the same S3 bucket.

S3 is used as a transfer point because it can commonly be used in areas where
network access is limited, such as within a private VPC.

This is a work in progress.
