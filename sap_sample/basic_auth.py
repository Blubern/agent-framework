"""
Basic SAP AI Core Authentication Example
Demonstrates how to obtain OAuth2 token from SAP AI Core
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_sap_access_token():
    """
    Get OAuth2 access token from SAP AI Core using client credentials flow.
    
    Returns:
        str: Access token for API authentication
    """
    auth_url = os.getenv('AICORE_AUTH_URL')
    client_id = os.getenv('AICORE_CLIENT_ID')
    client_secret = os.getenv('AICORE_CLIENT_SECRET')
    
    if not all([auth_url, client_id, client_secret]):
        raise ValueError("Missing required environment variables: AICORE_AUTH_URL, AICORE_CLIENT_ID, AICORE_CLIENT_SECRET")
    
    # Make OAuth2 token request
    response = requests.post(
        f"{auth_url}/oauth/token",
        auth=(client_id, client_secret),
        data={
            'grant_type': 'client_credentials'
        },
        timeout=30
    )
    
    response.raise_for_status()
    token_data = response.json()
    
    return token_data['access_token']


def test_sap_connection():
    """Test SAP AI Core connection with authentication"""
    try:
        # Get access token
        print("Obtaining access token from SAP AI Core...")
        token = get_sap_access_token()
        print(f"✓ Successfully obtained token: {token[:20]}...")
        
        # Test API connection
        base_url = os.getenv('AICORE_BASE_URL')
        resource_group = os.getenv('AICORE_RESOURCE_GROUP', 'default')
        
        headers = {
            'Authorization': f'Bearer {token}',
            'AI-Resource-Group': resource_group
        }
        
        print(f"\nTesting connection to {base_url}...")
        response = requests.get(
            f"{base_url}/v2/lm/deployments",
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        print("✓ Successfully connected to SAP AI Core!")
        print(f"Status Code: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("SAP AI Core Basic Authentication Test\n" + "="*50)
    test_sap_connection()