import sys
import os
from azure_keyvault_helper import AzureKeyVaultHelper

def get_variable(var_name):
    tenant_id = os.environ.get("AZURE_KV_TENANT_ID") if "AZURE_KV_TENANT_ID" in os.environ else ""
    client_id = os.environ.get("AZURE_KV_CLIENT_ID") if "AZURE_KV_CLIENT_ID" in os.environ else ""
    client_secret = os.environ.get("AZURE_KV_CLIENT_SECRET") if "AZURE_KV_CLIENT_SECRET" in os.environ else ""
    keyvault_id = os.environ.get("AZURE_KV_ID") if "AZURE_KV_ID" in os.environ else "CriaKeyVault"
    azure_helper = AzureKeyVaultHelper(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

    data = azure_helper.get_data(keyvault_id=keyvault_id, var_name=var_name)

    if not data:
        return ""
    return data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        var_name = sys.argv[1]
    else:
        print("Please provide variable name!")
        exit(-1)

    with open(var_name, 'w') as output:
        output.write(get_variable(var_name=var_name))
