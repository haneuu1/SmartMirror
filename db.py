import cv2
import requests
import boto3
import socket
import time
from serial import myserial

AWS_ACCESS_KEY_ID = "aws_access_key_id"
AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"
AWS_DEFAULT_REGION = 'region'
 
def upload_file(fpath, serialnum):
    times = time.strftime('%Y%m%d', time.localtime())
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)
    res = s3.upload_file(fpath, 'name', '{}-{}'.format(serialnum, times)+'.jpg')
    requests.get('http://0.0.0.0:5000/result/{}/{}'.format(serialnum, times))
