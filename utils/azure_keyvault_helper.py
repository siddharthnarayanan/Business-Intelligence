import logging

from azure.keyvault import KeyVaultId, KeyVaultClient, KeyVaultAuthentication
from azure.common.credentials import ServicePrincipalCredentials

logger = logging.getLogger(__name__)

class AzureKeyVaultHelper:
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id=client_id
        self.tenant_id=tenant_id
        self.client_secret=client_secret
        self.credentials = ServicePrincipalCredentials(
            client_id=self.client_id,
            secret=self.client_secret,
            tenant=self.tenant_id,
        )
        self.client = KeyVaultClient(self.credentials)

    def get_data(self, keyvault_id, var_name, var_version=None):
        try:
            secret_bundle = self.client.get_secret("https://%s.vault.azure.net/" % keyvault_id,
                                                   var_name, secret_version=var_version or KeyVaultId.version_none)
            return secret_bundle.value

        except Exception as ex:
            logger.error("Error occured when trying to fetch %s: %s" % (var_name, ex))
            return None
