import json
import base64
import hmac
import pytz
import hashlib
import datetime
import requests
import os

OMS_KEY = os.getenv('OMS_KEY', default='')
WORKSPACE_ID = os.getenv('OMS_WORKSPACE_ID', default='')
OMS_INSTANCE_ID = os.environ.get('OMS_INSTANCE_ID', default='unknown')

def _get_timestamp_in_rfc_1132():
    timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('GMT'))
    return timestamp.strftime("%a, %d %b %Y %H:%M:%S %Z")

def _calculate_signature(content_len, content_type, x_ms_date, key):
    sign_string = 'POST\n{}\n{}\nx-ms-date:{}\n/api/logs'.format(content_len, content_type, x_ms_date).encode('utf-8')
    signature = hmac.new(key, sign_string, digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def send_data_to_oms(data, log_type):
    data['instance_id'] = OMS_INSTANCE_ID
    data_string = json.dumps(data)
    content_type = 'application/json'
    content_len = len(data_string)
    x_ms_date = _get_timestamp_in_rfc_1132()
    key = base64.b64decode(OMS_KEY.encode('utf-8'))
    signature = _calculate_signature(content_len, content_type, x_ms_date, key)

    headers = {'Content-Length': str(content_len),
               'Content-Type': content_type,
               'x-ms-date': x_ms_date,
               'Log-Type': log_type,
               'Authorization': 'SharedKey {}:{}'.format(WORKSPACE_ID, signature)}

    return requests.post('https://{}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01'.format(WORKSPACE_ID), data=data_string, headers=headers)
