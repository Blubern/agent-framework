"""
Example using SAPTokenManager for authenticated requests
"""

import os
import requests
from dotenv import load_dotenv
from token_manager import SAPTokenManager

# Load environment variables
load_dotenv()

def main():
    """Example of using the token manager"""
    print("SAP AI Core Token Manager Example\n" + "="*50)
    
    # Initialize token manager
    token_manager = SAPTokenManager()
    
    # Make multiple requests - token will be reused
    base_url = os.getenv('AICORE_BASE_URL')
    
    print("\n1. First request - will obtain new token")
    headers = token_manager.get_auth_headers()
    print(f"Using token: {headers['Authorization'][:30]}...")
    
    response = requests.get(
        f"{base_url}/v2/lm/deployments",
        headers=headers,
        timeout=30
    )
    print(f"Response: {response.status_code}")
    
    print("\n2. Second request - will reuse token")
    headers = token_manager.get_auth_headers()
    print(f"Using token: {headers['Authorization'][:30]}...")
    
    response = requests.get(
        f"{base_url}/v2/lm/deployments",
        headers=headers,
        timeout=30
    )
    print(f"Response: {response.status_code}")
    
    print("\n3. Force refresh token")
    token_manager.force_refresh()
    headers = token_manager.get_auth_headers()
    print(f"New token: {headers['Authorization'][:30]}...")
    
    print("\n✓ Token manager working correctly!")


if __name__ == "__main__":
    main()