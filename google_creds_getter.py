from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from requests import HTTPError
from typing import List
class GoogleCreds:
    creds: None 
    def __init__(self, SCOPES: List[str]):
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        self.creds = flow.run_local_server(port=0)

    def get_service(self, service_name: str, service_version: str):
        service: Resource = build(service_name, service_version, credentials=self.creds)
        return service



