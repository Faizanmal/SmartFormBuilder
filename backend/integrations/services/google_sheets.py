"""
Google Sheets OAuth2 integration service
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
from django.urls import reverse
import json


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_oauth_flow(redirect_uri=None):
    """Create OAuth2 flow for Google Sheets"""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri or settings.GOOGLE_REDIRECT_URI],
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri or settings.GOOGLE_REDIRECT_URI
    )
    
    return flow


def get_authorization_url(state=None):
    """Get Google OAuth2 authorization URL"""
    flow = get_oauth_flow()
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return auth_url, state


def exchange_code_for_tokens(code, redirect_uri=None):
    """Exchange authorization code for access/refresh tokens"""
    flow = get_oauth_flow(redirect_uri)
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    
    return {
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }


def get_sheets_service(credentials_dict):
    """Create Google Sheets service from credentials"""
    credentials = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
    
    service = build('sheets', 'v4', credentials=credentials)
    return service


def create_spreadsheet(credentials_dict, title):
    """Create a new Google Spreadsheet"""
    service = get_sheets_service(credentials_dict)
    
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    
    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    return result.get('spreadsheetId')


def append_row_to_sheet(credentials_dict, spreadsheet_id, values):
    """Append a row to a Google Sheet"""
    service = get_sheets_service(credentials_dict)
    
    body = {
        'values': [values]
    }
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='Sheet1!A1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    return result


def get_spreadsheet_info(credentials_dict, spreadsheet_id):
    """Get spreadsheet metadata"""
    service = get_sheets_service(credentials_dict)
    
    result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {
        'title': result.get('properties', {}).get('title'),
        'url': result.get('spreadsheetUrl'),
        'sheets': [s.get('properties', {}).get('title') for s in result.get('sheets', [])]
    }
