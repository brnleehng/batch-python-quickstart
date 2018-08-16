from __future__ import print_function
import datetime
import io
import os
import sys
import time

try:
    input = raw_input
except NameError:
    pass

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels
import msrestazure.azure_active_directory
import msrest.authentication
from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
from azure.common.credentials import ServicePrincipalCredentials

metadata_dict = {}
def auth_callback(server, resource, scope):
    credentials = ServicePrincipalCredentials(
        client_id = metadata_dict['AZURE_CLIENT_ID'],
        secret = metadata_dict['AZURE_CLIENT_SECRET'],
        tenant = metadata_dict['AZURE_TENANT_ID'],
        resource = "https://vault.azure.net"
    )
    token = credentials.token
    return token['token_type'], token['access_token']

if __name__ == '__main__':
    token_provider = os.environ['AZ_BATCH_AUTHENTICATION_TOKEN']
    job_id = os.environ['AZ_BATCH_JOB_ID']
    batch_account_url = os.environ['AZ_BATCH_ACCOUNT_URL']
    
    token = {'access_token': token_provider}
    credentials = msrest.authentication.BasicTokenAuthentication(token)
    batch_client = batch.BatchServiceClient(
        credentials,
        base_url=batch_account_url)

    job = batch_client.job.get(job_id)

    for metadata in job.metadata:
        metadata_dict[metadata.name] = metadata.value

    client = KeyVaultClient(KeyVaultAuthentication(auth_callback))
    keyvault_url = os.environ['AZ_KEYVAULT_URL']
    secret_name = os.environ['AZ_KEYVAULT_SECRET_NAME']

    secret_bundle = client.get_secret(keyvault_url, secret_name, "")
    print(secret_bundle)
    print(secret_bundle.value)
    
