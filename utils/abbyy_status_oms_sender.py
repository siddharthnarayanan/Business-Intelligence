from abbyy_license_status import abbyy_license_data
from oms_data_sender import send_data_to_oms
from flask import current_app

OMS_ABBYY_LICENSE_LOG_TYPE = 'abbyy_license_status'

def send_abbyy_stats_to_oms():
    license_data = abbyy_license_data()
    response = send_data_to_oms(license_data, OMS_ABBYY_LICENSE_LOG_TYPE)
    if response.ok:
        current_app.logger.info('Abbyy license status update posted to OMS')
    else:
        current_app.logger.warning('OMS update failed')
