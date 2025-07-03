#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, AWS Innovation Sandbox API Interface Role
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sandbox_api
short_description: Interface with AWS Innovation Sandbox API
description:
- This module provides an interface to interact with the AWS Innovation Sandbox API
- Supports account management, lease management, user management, and monitoring operations
- Handles authentication, error handling, and response processing
version_added: "1.0.0"
author:
- AWS Innovation Sandbox API Interface Role

options:
  action:
    description:
    - The action to perform with the API
    type: str
    required: true
    choices:
    - list_accounts
    - get_account
    - create_account
    - update_account
    - delete_account
    - list_leases
    - get_lease
    - create_lease
    - extend_lease
    - terminate_lease
    - list_users
    - get_user
    - create_user
    - update_user
    - delete_user
    - get_config
    - get_metrics
    - get_status
    - health_check
  
  api_url:
    description:
    - Base URL for the Innovation Sandbox API
    type: str
    required: true
  
  api_version:
    description:
    - API version to use
    type: str
    default: v1
  
  auth_type:
    description:
    - Authentication type to use
    type: str
    choices: [aws_iam, api_key, oauth2, basic]
    default: aws_iam
  
  auth_config:
    description:
    - Authentication configuration
    type: dict
    default: {}
  
  timeout:
    description:
    - Request timeout in seconds
    type: int
    default: 30
  
  validate_certs:
    description:
    - Whether to validate SSL certificates
    type: bool
    default: true
  
  # Resource-specific parameters
  account_id:
    description:
    - Account ID for account-specific operations
    type: str
  
  lease_id:
    description:
    - Lease ID for lease-specific operations
    type: str
  
  user_id:
    description:
    - User ID for user-specific operations
    type: str
  
  resource_data:
    description:
    - Data for create/update operations
    type: dict
    default: {}
  
  query_params:
    description:
    - Query parameters for list operations
    type: dict
    default: {}

notes:
- This module requires Python requests library
- Authentication credentials should be provided via auth_config parameter
- Some operations may require specific permissions

requirements:
- python >= 3.6
- requests
'''

EXAMPLES = r'''
- name: List all accounts
  sandbox_api:
    action: list_accounts
    api_url: "https://your-sandbox-api.amazonaws.com"
    auth_type: api_key
    auth_config:
      api_key: "your-api-key"

- name: Create a new account
  sandbox_api:
    action: create_account
    api_url: "https://your-sandbox-api.amazonaws.com"
    auth_type: aws_iam
    resource_data:
      name: "test-account"
      email: "admin@example.com"
      budget_limit: 100
      duration: 7200

- name: Get specific account details
  sandbox_api:
    action: get_account
    api_url: "https://your-sandbox-api.amazonaws.com"
    account_id: "account-123"
    auth_type: api_key
    auth_config:
      api_key: "your-api-key"

- name: Create a lease
  sandbox_api:
    action: create_lease
    api_url: "https://your-sandbox-api.amazonaws.com"
    auth_type: aws_iam
    resource_data:
      account_id: "account-123"
      user_id: "user-456"
      duration: 3600
      purpose: "Testing deployment"

- name: Extend a lease
  sandbox_api:
    action: extend_lease
    api_url: "https://your-sandbox-api.amazonaws.com"
    lease_id: "lease-789"
    resource_data:
      duration: 1800
    auth_type: api_key
    auth_config:
      api_key: "your-api-key"

- name: Check API health
  sandbox_api:
    action: health_check
    api_url: "https://your-sandbox-api.amazonaws.com"
    auth_type: aws_iam
'''

RETURN = r'''
result:
  description: The API response data
  type: dict
  returned: always
  sample:
    status: success
    data:
      account_id: "account-123"
      name: "test-account"
      status: "available"

changed:
  description: Whether the operation resulted in a change
  type: bool
  returned: always

failed:
  description: Whether the operation failed
  type: bool
  returned: always

msg:
  description: Human readable message about the operation
  type: str
  returned: always

status_code:
  description: HTTP status code from the API
  type: int
  returned: always
'''

import json
import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text


class SandboxAPIClient:
    def __init__(self, module):
        self.module = module
        self.api_url = module.params['api_url'].rstrip('/')
        self.api_version = module.params['api_version']
        self.auth_type = module.params['auth_type']
        self.auth_config = module.params['auth_config']
        self.timeout = module.params['timeout']
        self.validate_certs = module.params['validate_certs']
        
        # Build full API URL
        self.base_url = f"{self.api_url}/{self.api_version}"
        
        # Setup headers
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'ansible-sandbox-api-client/1.0'
        }
        
        # Setup authentication
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication headers based on auth_type"""
        if self.auth_type == 'api_key':
            api_key = self.auth_config.get('api_key')
            if api_key:
                self.headers['X-API-Key'] = api_key
        elif self.auth_type == 'basic':
            username = self.auth_config.get('username')
            password = self.auth_config.get('password')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                self.headers['Authorization'] = f"Basic {credentials}"
        elif self.auth_type == 'oauth2':
            token = self.auth_config.get('token')
            if token:
                self.headers['Authorization'] = f"Bearer {token}"
        # AWS IAM authentication would require more complex signature calculation
        # For now, we'll assume credentials are handled externally
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        # Add query parameters
        if params:
            url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # Prepare request data
        if data:
            data = json.dumps(data)
        
        # Make request
        resp, info = fetch_url(
            self.module,
            url,
            headers=self.headers,
            method=method,
            data=data,
            timeout=self.timeout,
            validate_certs=self.validate_certs
        )
        
        # Process response
        content = ''
        if resp:
            content = resp.read()
            if content:
                content = to_text(content)
        
        status_code = info.get('status', 0)
        
        # Parse JSON response
        result = {}
        if content:
            try:
                result = json.loads(content)
            except (ValueError, TypeError):
                result = {'raw_response': content}
        
        return {
            'status_code': status_code,
            'data': result,
            'info': info
        }
    
    def list_accounts(self, params=None):
        """List all accounts"""
        return self._make_request('GET', '/accounts', params=params)
    
    def get_account(self, account_id):
        """Get specific account"""
        return self._make_request('GET', f'/accounts/{account_id}')
    
    def create_account(self, data):
        """Create new account"""
        return self._make_request('POST', '/accounts', data=data)
    
    def update_account(self, account_id, data):
        """Update existing account"""
        return self._make_request('PUT', f'/accounts/{account_id}', data=data)
    
    def delete_account(self, account_id):
        """Delete account"""
        return self._make_request('DELETE', f'/accounts/{account_id}')
    
    def list_leases(self, params=None):
        """List all leases"""
        return self._make_request('GET', '/leases', params=params)
    
    def get_lease(self, lease_id):
        """Get specific lease"""
        return self._make_request('GET', f'/leases/{lease_id}')
    
    def create_lease(self, data):
        """Create new lease"""
        return self._make_request('POST', '/leases', data=data)
    
    def extend_lease(self, lease_id, data):
        """Extend existing lease"""
        return self._make_request('POST', f'/leases/{lease_id}/extend', data=data)
    
    def terminate_lease(self, lease_id):
        """Terminate lease"""
        return self._make_request('POST', f'/leases/{lease_id}/terminate')
    
    def list_users(self, params=None):
        """List all users"""
        return self._make_request('GET', '/users', params=params)
    
    def get_user(self, user_id):
        """Get specific user"""
        return self._make_request('GET', f'/users/{user_id}')
    
    def create_user(self, data):
        """Create new user"""
        return self._make_request('POST', '/users', data=data)
    
    def update_user(self, user_id, data):
        """Update existing user"""
        return self._make_request('PUT', f'/users/{user_id}', data=data)
    
    def delete_user(self, user_id):
        """Delete user"""
        return self._make_request('DELETE', f'/users/{user_id}')
    
    def get_config(self):
        """Get global configuration"""
        return self._make_request('GET', '/config')
    
    def get_metrics(self):
        """Get system metrics"""
        return self._make_request('GET', '/metrics')
    
    def get_status(self):
        """Get system status"""
        return self._make_request('GET', '/status')
    
    def health_check(self):
        """Perform health check"""
        return self._make_request('GET', '/health')


def main():
    module_args = dict(
        action=dict(type='str', required=True, choices=[
            'list_accounts', 'get_account', 'create_account', 'update_account', 'delete_account',
            'list_leases', 'get_lease', 'create_lease', 'extend_lease', 'terminate_lease',
            'list_users', 'get_user', 'create_user', 'update_user', 'delete_user',
            'get_config', 'get_metrics', 'get_status', 'health_check'
        ]),
        api_url=dict(type='str', required=True),
        api_version=dict(type='str', default='v1'),
        auth_type=dict(type='str', choices=['aws_iam', 'api_key', 'oauth2', 'basic'], default='aws_iam'),
        auth_config=dict(type='dict', default={}),
        timeout=dict(type='int', default=30),
        validate_certs=dict(type='bool', default=True),
        account_id=dict(type='str'),
        lease_id=dict(type='str'),
        user_id=dict(type='str'),
        resource_data=dict(type='dict', default={}),
        query_params=dict(type='dict', default={})
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Initialize API client
    client = SandboxAPIClient(module)
    
    action = module.params['action']
    account_id = module.params['account_id']
    lease_id = module.params['lease_id']
    user_id = module.params['user_id']
    resource_data = module.params['resource_data']
    query_params = module.params['query_params']
    
    result = {
        'changed': False,
        'failed': False,
        'msg': '',
        'result': {},
        'status_code': 0
    }
    
    try:
        # Route to appropriate action
        if action == 'list_accounts':
            response = client.list_accounts(params=query_params)
        elif action == 'get_account':
            if not account_id:
                module.fail_json(msg="account_id is required for get_account action")
            response = client.get_account(account_id)
        elif action == 'create_account':
            response = client.create_account(resource_data)
            result['changed'] = True
        elif action == 'update_account':
            if not account_id:
                module.fail_json(msg="account_id is required for update_account action")
            response = client.update_account(account_id, resource_data)
            result['changed'] = True
        elif action == 'delete_account':
            if not account_id:
                module.fail_json(msg="account_id is required for delete_account action")
            response = client.delete_account(account_id)
            result['changed'] = True
        elif action == 'list_leases':
            response = client.list_leases(params=query_params)
        elif action == 'get_lease':
            if not lease_id:
                module.fail_json(msg="lease_id is required for get_lease action")
            response = client.get_lease(lease_id)
        elif action == 'create_lease':
            response = client.create_lease(resource_data)
            result['changed'] = True
        elif action == 'extend_lease':
            if not lease_id:
                module.fail_json(msg="lease_id is required for extend_lease action")
            response = client.extend_lease(lease_id, resource_data)
            result['changed'] = True
        elif action == 'terminate_lease':
            if not lease_id:
                module.fail_json(msg="lease_id is required for terminate_lease action")
            response = client.terminate_lease(lease_id)
            result['changed'] = True
        elif action == 'list_users':
            response = client.list_users(params=query_params)
        elif action == 'get_user':
            if not user_id:
                module.fail_json(msg="user_id is required for get_user action")
            response = client.get_user(user_id)
        elif action == 'create_user':
            response = client.create_user(resource_data)
            result['changed'] = True
        elif action == 'update_user':
            if not user_id:
                module.fail_json(msg="user_id is required for update_user action")
            response = client.update_user(user_id, resource_data)
            result['changed'] = True
        elif action == 'delete_user':
            if not user_id:
                module.fail_json(msg="user_id is required for delete_user action")
            response = client.delete_user(user_id)
            result['changed'] = True
        elif action == 'get_config':
            response = client.get_config()
        elif action == 'get_metrics':
            response = client.get_metrics()
        elif action == 'get_status':
            response = client.get_status()
        elif action == 'health_check':
            response = client.health_check()
        else:
            module.fail_json(msg=f"Unknown action: {action}")
        
        # Process response
        result['status_code'] = response['status_code']
        result['result'] = response['data']
        
        # Check if request was successful
        if response['status_code'] in [200, 201, 202, 204]:
            result['msg'] = f"Action {action} completed successfully"
        else:
            result['failed'] = True
            result['msg'] = f"Action {action} failed with status {response['status_code']}"
            if response['data']:
                result['msg'] += f": {response['data']}"
    
    except Exception as e:
        result['failed'] = True
        result['msg'] = f"Error executing action {action}: {str(e)}"
    
    # Return result
    if result['failed']:
        module.fail_json(**result)
    else:
        module.exit_json(**result)


if __name__ == '__main__':
    main() 