from appwrite.client import Client
from appwrite.services.databases import Databases
from utils.config import (
    APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID, APPWRITE_API_KEY
)

_client = Client()
_client.set_endpoint(APPWRITE_ENDPOINT)
_client.set_project(APPWRITE_PROJECT_ID)
_client.set_key(APPWRITE_API_KEY)

db: Databases = Databases(_client)
