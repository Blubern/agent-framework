"""
SAP AI Core Token Manager
Handles OAuth2 token retrieval and automatic refresh
"""

import os
import requests
import threading
from datetime import datetime, timedelta
from typing import Optional


class SAPTokenManager:
    """
    Manages OAuth2 tokens for SAP AI Core with automatic refresh.
    Thread-safe implementation.
    """
    
    def __init__(self):
        self.token: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.lock = threading.Lock()
        
        # Load credentials from environment
        self.auth_url = os.getenv('AICORE_AUTH_URL')
        self.client_id = os.getenv('AICORE_CLIENT_ID')
        self.client_secret = os.getenv('AICORE_CLIENT_SECRET')
        
        if not all([self.auth_url, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required environment variables: "
                "AICORE_AUTH_URL, AICORE_CLIENT_ID, AICORE_CLIENT_SECRET"
            )
    
    def get_token(self) -> str:
        """
        Get current access token, refreshing if necessary.
        
        Returns:
            str: Valid access token
        """
        with self.lock:
            # Check if token needs refresh
            if not self.token or not self.expires_at or datetime.now() >= self.expires_at:
                self._refresh_token()
            return self.token
    
    def _refresh_token(self) -> None:
        """Internal method to refresh the access token"""
        print("Refreshing SAP AI Core access token...")
        
        response = requests.post(
            f"{self.auth_url}/oauth/token",
            auth=(self.client_id, self.client_secret),
            data={'grant_type': 'client_credentials'},
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        self.token = data['access_token']
        # Tokens typically expire in 3600 seconds, refresh 5 minutes early
        expires_in = data.get('expires_in', 3600)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        
        print(f"✓ Token refreshed, expires at {self.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_auth_headers(self, resource_group: Optional[str] = None) -> dict:
        """
        Get authentication headers for SAP AI Core API requests.
        
        Args:
            resource_group: SAP AI Core resource group (defaults to env var or 'default')
            
        Returns:
            dict: Headers with Authorization and AI-Resource-Group
        """
        if resource_group is None:
            resource_group = os.getenv('AICORE_RESOURCE_GROUP', 'default')
        
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'AI-Resource-Group': resource_group,
            'Content-Type': 'application/json'
        }
    
    def force_refresh(self) -> None:
        """Force token refresh immediately"""
        with self.lock:
            self._refresh_token()