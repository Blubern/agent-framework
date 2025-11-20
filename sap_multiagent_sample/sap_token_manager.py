"""
SAP AI Core Token Manager for Multi-Agent Systems
Centralized OAuth2 token management with automatic refresh and thread safety
"""

import os
import requests
import threading
from datetime import datetime, timedelta
from typing import Optional


class SAPTokenManager:
    """
    Manages OAuth2 tokens for SAP AI Core with automatic refresh.
    Thread-safe implementation suitable for multi-agent systems.
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
        Thread-safe for concurrent agent access.
        
        Returns:
            str: Valid access token
        """
        with self.lock:
            # Check if token needs refresh (refresh 5 minutes before expiration)
            if not self.token or not self.expires_at or datetime.now() >= self.expires_at:
                self._refresh_token()
            return self.token
    
    def _refresh_token(self) -> None:
        """Internal method to refresh the access token"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Refreshing SAP AI Core access token...")
        
        try:
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
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Token refreshed, expires at {self.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Token refresh failed: {e}")
            raise
    
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
    
    def is_token_valid(self) -> bool:
        """
        Check if current token is valid without refreshing.
        
        Returns:
            bool: True if token exists and hasn't expired
        """
        if not self.token or not self.expires_at:
            return False
        return datetime.now() < self.expires_at


# Singleton instance for shared use across agents
_token_manager_instance: Optional[SAPTokenManager] = None
_instance_lock = threading.Lock()


def get_token_manager() -> SAPTokenManager:
    """
    Get singleton instance of SAPTokenManager.
    Thread-safe singleton pattern for multi-agent systems.
    
    Returns:
        SAPTokenManager: Shared token manager instance
    """
    global _token_manager_instance
    
    if _token_manager_instance is None:
        with _instance_lock:
            # Double-check locking pattern
            if _token_manager_instance is None:
                _token_manager_instance = SAPTokenManager()
    
    return _token_manager_instance
