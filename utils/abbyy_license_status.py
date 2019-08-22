import subprocess

LICENSE_INIT_CMD = '/usr/bin/CommandLineInterface'
LICENSE_NUMBER_CMD = '/opt/ABBYY/FREngine12/Bin/LicenseManager.Console --listAvailableLicenses'
RESPONSE_ITEMS = ['Serial Number', 'Expiration Date', 'Quantity', 'Remains']

def abbyy_license_data():
    subprocess.check_output(LICENSE_INIT_CMD, shell=True)
    license_number = subprocess.check_output(LICENSE_NUMBER_CMD, shell=True).decode('utf-8').rstrip()
    if license_number:
        result = {}
        license_params_cmd = "/opt/ABBYY/FREngine12/Bin/LicenseManager.Console --showLicenseParameters={}".format(license_number)
        for line in subprocess.check_output(license_params_cmd, shell=True).splitlines():
            decoded_line = line.decode('utf-8').split(':')
            if len(decoded_line) > 1:
                key = decoded_line[0].strip()
                value = decoded_line[1].strip()
                if key in RESPONSE_ITEMS:
                    result[key] = value
        return result
