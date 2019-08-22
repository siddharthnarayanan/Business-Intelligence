import os
import requests
import datetime
import pytz
import hmac
import hashlib
import base64
import urllib
from bson import ObjectId
from bson.json_util import dumps
from pymongo import MongoClient, ASCENDING
from azure_keyvault_helper import AzureKeyVaultHelper

WORKSPACE_ID = os.getenv('OMS_WORKSPACE_ID', default='')
OMS_KEY = os.getenv('OMS_KEY', default='')
PERIOD_SECONDS = int(os.getenv('OMS_REPORT_PERIOD_SECONDS', default=1800))
OMS_INSTANCE_ID = os.environ.get("OMS_INSTANCE_ID") if "OMS_INSTANCE_ID" in os.environ else "unknown"

AZURE_DEPLOYMENT = True if "CLOUD_DEPLOY" in os.environ else False
MONGO_HOST = os.environ.get("MONGO_HOST") if "MONGO_HOST" in os.environ else "localhost"
MONGO_PORT = os.environ.get("MONGO_PORT") if "MONGO_PORT" in os.environ else "27017"
MONGO_USER = os.environ.get("MONGO_USER") if "MONGO_USER" in os.environ else "cria"
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD") if "MONGO_PASSWORD" in os.environ else "L0gin123*"
MONGO_SSL = os.environ.get("MONGO_SSL") if "MONGO_SSL" in os.environ else "true"
MONGO_AUTH = os.environ.get("MONGO_AUTH") if "MONGO_AUTH" in os.environ else "admin"
MONGO_DBNAME = os.environ.get("MONGO_DBNAME") if "MONGO_DBNAME" in os.environ else "metadata"
MONGO_SERVER = ""
MONGO_AZURE = True if "MONGO_AZURE" in os.environ else False
MONGO_POD = True if "MONGO_POD" in os.environ else False

azure_helper = None
KEYVAULT_ID = ""

# Read data from KeyVault
if AZURE_DEPLOYMENT:
    TENANT_ID = os.environ.get("AZURE_KV_TENANT_ID") if "AZURE_KV_TENANT_ID" in os.environ else ""
    CLIENT_ID = os.environ.get("AZURE_KV_CLIENT_ID") if "AZURE_KV_CLIENT_ID" in os.environ else ""
    CLIENT_SECRET = os.environ.get("AZURE_KV_CLIENT_SECRET") if "AZURE_KV_CLIENT_SECRET" in os.environ else ""
    KEYVAULT_ID = os.environ.get("AZURE_KV_ID") if "AZURE_KV_ID" in os.environ else "CriaKeyVault"
    azure_helper = AzureKeyVaultHelper(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, tenant_id=TENANT_ID)
    MONGO_USER = azure_helper.get_data(keyvault_id=KEYVAULT_ID, var_name='MONGO-USER') or ""
    MONGO_PASSWORD = azure_helper.get_data(keyvault_id=KEYVAULT_ID, var_name='MONGO-PASSWORD') or ""
    AZURE_KEY = azure_helper.get_data(keyvault_id=KEYVAULT_ID, var_name='AZURE-KEY') or ""

    MONGO_SERVER = "mongodb://"+urllib.parse.quote_plus(MONGO_USER)+":"+urllib.parse.quote_plus(MONGO_PASSWORD)+"@"+MONGO_HOST+":"+str(MONGO_PORT)+"/?ssl=true&replicaSet=globaldb"

if MONGO_AZURE or not AZURE_DEPLOYMENT:
    if MONGO_SSL.lower() == 'true':
        MONGO_SERVER = "mongodb://"+urllib.parse.quote_plus(MONGO_USER)+":"+urllib.parse.quote_plus(MONGO_PASSWORD)+"@"+MONGO_HOST+":"+str(MONGO_PORT)+"/"+MONGO_DBNAME+"?authSource="+MONGO_AUTH+"&authMechanism=SCRAM-SHA-1&ssl=true&ssl_cert_reqs=CERT_NONE"
    else:
        MONGO_SERVER = "mongodb://"+urllib.parse.quote_plus(MONGO_USER)+":"+urllib.parse.quote_plus(MONGO_PASSWORD)+"@"+MONGO_HOST+":"+str(MONGO_PORT)+"/"+MONGO_DBNAME+"?authSource="+MONGO_AUTH+"&authMechanism=SCRAM-SHA-1"

if MONGO_POD:
    MONGO_SERVER = "mongodb://"+urllib.parse.quote_plus(MONGO_USER)+":"+urllib.parse.quote_plus(MONGO_PASSWORD)+"@"+MONGO_HOST+":"+str(MONGO_PORT)+"/"+MONGO_DBNAME+"?authSource="+MONGO_AUTH+"&authMechanism=SCRAM-SHA-1&ssl=false&replicaSet=rs0"

def get_timestamp_in_rfc_1132():
    timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('GMT'))
    return timestamp.strftime("%a, %d %b %Y %H:%M:%S %Z")

def calculate_signature(content_len, content_type, x_ms_date, key):
    sign_string = 'POST\n{}\n{}\nx-ms-date:{}\n/api/logs'.format(content_len, content_type, x_ms_date).encode('utf-8')
    signature = hmac.new(key, sign_string, digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode()
 
def send_data_to_oms(data, log_type):
    data_string = dumps(data)
    content_type = 'application/json'
    content_len = len(data_string)
    x_ms_date = get_timestamp_in_rfc_1132()

    key = base64.b64decode(OMS_KEY.encode('utf-8'))
    signature = calculate_signature(content_len, content_type, x_ms_date, key)
    headers = {'Content-Length': str(content_len),
               'Content-Type': content_type,
               'x-ms-date': x_ms_date,
               'Log-Type': log_type,
               'Authorization': 'SharedKey {}:{}'.format(WORKSPACE_ID, signature)}

    response = requests.post('https://{}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01'.format(WORKSPACE_ID), data=data_string, headers=headers)


def send_rendering_timings_to_oms():
    client = MongoClient(MONGO_SERVER)
    db = client[MONGO_DBNAME]
    contracts = db.contracts.find()

    data_to_send = []
    for c in contracts:
        target_datetime = datetime.datetime.now() - datetime.timedelta(seconds=PERIOD_SECONDS)
        events = list(db.logging_events.find({'metadata': {'contract': c['_id']}, 'action': 'Render Unitvals', 'timestamp': {'$gt': target_datetime}}).sort([("timestamp", ASCENDING)]))
        for event in events:
            report_entry = {
                "instance_id": OMS_INSTANCE_ID,
                "file_name": c['file_name'],
                "page_count": len(c['contract_pdf']),
                "timestamp": event['timestamp'],
                "timing": int(event['message'])
            }
            data_to_send.append(report_entry)
    print('Sending report ({} entries)'.format(len(data_to_send)))
    send_data_to_oms(data_to_send, log_type='performance_uoa_rendering_timings')


def send_events_to_oms():
    client = MongoClient(MONGO_SERVER)
    db = client[MONGO_DBNAME]
    contracts = db.contracts.find()

    data_to_send = []
    for c in contracts:
        events = list(db.logging_events.find({'metadata': {'contract': c['_id']}}).sort([("timestamp", ASCENDING)]))
        actions = {
            "Contract Entry Created": None,
            "OCR start": None,
            "OCR finish": None,
            "EE start": None,
            "EE finish": None,
            "Apply Models start": None,
            "Apply Models finish": None,
            "Processing Complete": None,
        }

        for e in events:
            if e['action'] in actions:
                actions[e['action']] = e['timestamp']

                if e['action'] == 'Apply Models finish' and not actions['Processing Complete']:
                    actions['Processing Complete'] = e['timestamp']

        report_entry = {
            "instance_id": OMS_INSTANCE_ID,
            "file_name": c['file_name'],
            "page_count": len(c['contract_pdf']),
            "processing_started": actions['Contract Entry Created'] or None,
            "ocr_started": actions['OCR start'] or None,
            "ocr_finished": actions['OCR finish'] or None,
            "ocr_time": None,
            "ee_started": actions["EE start"] or None,
            "ee_finished": actions["EE finish"] or None,
            "ee_time": None,
            "am_started": actions["Apply Models start"] or None,
            "am_finished": actions["Apply Models finish"] or None,
            "am_time": None,
            "processing_finished": actions['Processing Complete'] or None,
        }
        if actions['OCR start'] and actions['OCR finish']:
            report_entry['ocr_time'] = (actions['OCR finish'] - actions['OCR start']).total_seconds()

        if actions['EE start'] and actions['EE finish']:
            report_entry['ee_time'] = (actions['EE finish'] - actions['EE start']).total_seconds()

        if actions['Apply Models start'] and actions['Apply Models finish']:
            report_entry['am_time'] = (actions['Apply Models finish'] - actions['Apply Models start']).total_seconds()

        if actions['Contract Entry Created'] and actions['Processing Complete']:
            report_entry['processing_time'] = (actions['Processing Complete'] - actions['Contract Entry Created']).total_seconds()

        try:
            for k in report_entry:
                if not report_entry[k]:
                    raise Exception("Not all the data collected: no {}".format(k))
        except Exception as ex:
            print("Skipped contract {} due to error: {}".format(c['file_name'], ex))
        else:
            print('Added contract {} to the report'.format(c['file_name']))
            data_to_send.append(report_entry)

    print('Sending report ({} entries)'.format(len(data_to_send)))
    send_data_to_oms(data_to_send, log_type='performance_timings_simple_full')

if __name__ == '__main__':
    send_events_to_oms()
    send_rendering_timings_to_oms()
