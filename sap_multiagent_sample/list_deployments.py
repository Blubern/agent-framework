# Copyright (c) Microsoft. All rights reserved.
"""
List SAP AI Core Deployments

Retrieves and displays all available deployments from SAP AI Core,
showing deployment ID, name, status, and model information.
"""

import os
import requests
from dotenv import load_dotenv
from sap_token_manager import get_token_manager

# Load environment variables
load_dotenv()


def list_deployments():
    """List all SAP AI Core deployments with details"""
    print("=" * 100)
    print("SAP AI Core Deployments")
    print("=" * 100)
    
    # Get authentication
    token_manager = get_token_manager()
    base_url = os.getenv('AICORE_BASE_URL')
    resource_group = os.getenv('AICORE_RESOURCE_GROUP', 'default')
    
    if not base_url:
        print("Error: AICORE_BASE_URL not set in environment")
        return
    
    # Get deployments list
    headers = token_manager.get_auth_headers(resource_group)
    
    try:
        print(f"\nFetching deployments from: {base_url}/v2/lm/deployments")
        print(f"Resource Group: {resource_group}\n")
        
        response = requests.get(
            f"{base_url}/v2/lm/deployments",
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        deployments = data.get('resources', [])
        
        if not deployments:
            print("No deployments found.")
            return
        
        print(f"Found {len(deployments)} deployment(s)\n")
        print("-" * 100)
        
        # Display deployments in a formatted table
        running_deployments = []
        stopped_deployments = []
        
        for deployment in deployments:
            deployment_info = {
                'id': deployment.get('id', 'N/A'),
                'name': deployment.get('configurationName', 'N/A'),
                'status': deployment.get('status', 'N/A'),
                'scenario': deployment.get('scenarioId', 'N/A'),
                'created': deployment.get('createdAt', 'N/A'),
                'modified': deployment.get('modifiedAt', 'N/A')
            }
            
            if deployment_info['status'] == 'RUNNING':
                running_deployments.append(deployment_info)
            else:
                stopped_deployments.append(deployment_info)
        
        # Display running deployments first
        if running_deployments:
            print("\nRUNNING DEPLOYMENTS:")
            print("=" * 100)
            for dep in running_deployments:
                print(f"\nID:       {dep['id']}")
                print(f"Name:     {dep['name']}")
                print(f"Status:   {dep['status']}")
                print(f"Scenario: {dep['scenario']}")
                print(f"Created:  {dep['created']}")
                print(f"Modified: {dep['modified']}")
                print("-" * 100)
        
        # Display stopped deployments
        if stopped_deployments:
            print("\n\nSTOPPED DEPLOYMENTS:")
            print("=" * 100)
            for dep in stopped_deployments:
                print(f"\nID:       {dep['id']}")
                print(f"Name:     {dep['name']}")
                print(f"Status:   {dep['status']}")
                print(f"Scenario: {dep['scenario']}")
                print(f"Created:  {dep['created']}")
                print(f"Modified: {dep['modified']}")
                print("-" * 100)
        
        # Summary
        print("\n" + "=" * 100)
        print(f"SUMMARY: {len(running_deployments)} running, {len(stopped_deployments)} stopped")
        print("=" * 100)
        
        # Quick reference for copying
        if running_deployments:
            print("\nQUICK REFERENCE - Running Deployment IDs:")
            for dep in running_deployments:
                print(f"  {dep['id']:25} # {dep['name']}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching deployments: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    list_deployments()
