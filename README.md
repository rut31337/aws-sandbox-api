# AWS Innovation Sandbox API Interface Role

This Ansible role provides a comprehensive interface for interacting with the AWS Innovation Sandbox API. It supports account management, lease management, user management, and monitoring operations with built-in error handling, authentication, and response processing.

## Features

- **Account Management**: Create, list, get, update, and delete sandbox accounts
- **Lease Management**: Create, extend, terminate, and monitor account leases
- **User Management**: Create, list, get, update, and delete users
- **Configuration Management**: Retrieve and manage global configuration settings
- **Monitoring**: Health checks, metrics, and status monitoring
- **Multiple Authentication Methods**: API key, Basic auth, OAuth2, and AWS IAM
- **Error Handling**: Retry logic, rate limiting, and circuit breaker patterns
- **Custom Module**: Includes a custom Ansible module for direct API interactions
- **Comprehensive Logging**: Detailed logging and notification capabilities

## Requirements

- Ansible >= 2.12
- Python >= 3.6
- Access to AWS Innovation Sandbox API
- Valid API credentials

## Installation

Clone this repository into your roles directory:

```bash
git clone https://github.com/your-org/aws-sandbox-api-role.git roles/aws-sandbox-api
```

Or download and extract the role to your roles directory:

```bash
# Download the role
wget https://github.com/your-org/aws-sandbox-api-role/archive/main.zip
unzip main.zip -d roles/
mv roles/aws-sandbox-api-role-main roles/aws-sandbox-api
```

## Dependencies

This role depends on the following Ansible collections:
- `ansible.posix >= 1.0.0`
- `community.general >= 5.0.0`

Install dependencies:

```bash
ansible-galaxy collection install ansible.posix community.general
```

## Role Variables

### Required Variables

```yaml
sandbox_api:
  base_url: "https://your-sandbox-api.amazonaws.com"
  auth:
    type: "api_key"  # or "aws_iam", "basic", "oauth2"
    api_key: "your-api-key"
```

### Authentication Configuration

#### API Key Authentication
```yaml
sandbox_api:
  auth:
    type: "api_key"
    api_key: "your-api-key"
```

#### AWS IAM Authentication
```yaml
sandbox_api:
  auth:
    type: "aws_iam"
    role_arn: "arn:aws:iam::123456789012:role/SandboxAPIRole"
```

#### Basic Authentication
```yaml
sandbox_api:
  auth:
    type: "basic"
    basic:
      username: "your-username"
      password: "your-password"
```

#### OAuth2 Authentication
```yaml
sandbox_api:
  auth:
    type: "oauth2"
    oauth2:
      client_id: "your-client-id"
      client_secret: "your-client-secret"
      token_url: "https://auth.example.com/oauth/token"
      scope: "sandbox:read sandbox:write"
```

### Operation Variables

Set the `sandbox_action` variable to specify the operation:

```yaml
sandbox_action: "list_accounts"  # or any supported action
```

### Supported Actions

- **Account Management**: `list_accounts`, `get_account`, `create_account`, `update_account`, `delete_account`
- **Lease Management**: `list_leases`, `get_lease`, `create_lease`, `extend_lease`, `terminate_lease`
- **User Management**: `list_users`, `get_user`, `create_user`, `update_user`, `delete_user`
- **Configuration**: `get_config`
- **Monitoring**: `get_metrics`, `get_status`, `health_check`

### Configuration Variables

```yaml
# API Configuration
sandbox_api:
  base_url: "https://your-sandbox-api.amazonaws.com"
  version: "v1"
  timeout: 30
  retries: 3
  retry_delay: 5
  ssl:
    verify: true
  headers:
    User-Agent: "ansible-sandbox-client/1.0"

# Account Defaults
sandbox_accounts:
  default_lease_duration: 7200  # 2 hours
  default_budget_limit: 100
  default_budget_currency: "USD"
  auto_cleanup: true
  cleanup_delay: 300

# Lease Defaults
sandbox_leases:
  default_duration: 7200
  max_duration: 28800
  min_duration: 300
  allow_extension: true
  max_extensions: 2
  extension_increment: 3600

# User Defaults
sandbox_users:
  default_role: "SandboxUser"
  default_permissions:
    - "CanCreateLease"
    - "CanViewOwnLeases"
    - "CanExtendLease"
    - "CanTerminateLease"

# Monitoring Configuration
sandbox_monitoring:
  cloudwatch:
    enabled: true
    log_group: "/aws/innovation-sandbox/api"
    metrics_namespace: "InnovationSandbox"
  logging:
    level: "INFO"
    include_request_body: false
    include_response_body: false
  health_check:
    enabled: true
    interval: 300
    timeout: 10
    endpoint: "/health"

# Error Handling
sandbox_error_handling:
  retry_on_errors: [429, 500, 502, 503, 504]
  rate_limit:
    enabled: true
    requests_per_second: 10
    burst_size: 20
  circuit_breaker:
    enabled: true
    failure_threshold: 5
    recovery_timeout: 60
    half_open_max_calls: 3
```

## Usage Examples

### Basic Health Check

```yaml
- name: Check API health
  include_role:
    name: aws-sandbox-api
  vars:
    sandbox_action: "health_check"
```

### List All Accounts

```yaml
- name: List all accounts
  include_role:
    name: aws-sandbox-api
  vars:
    sandbox_action: "list_accounts"
```

### Create a New Account

```yaml
- name: Create a new account
  include_role:
    name: aws-sandbox-api
  vars:
    sandbox_action: "create_account"
    sandbox_account_name: "test-account"
    sandbox_account_email: "admin@example.com"
    sandbox_account_budget: 100
    sandbox_account_duration: 7200
    sandbox_account_tags:
      Environment: "dev"
      Purpose: "testing"
```

### Create a Lease

```yaml
- name: Create a lease
  include_role:
    name: aws-sandbox-api
  vars:
    sandbox_action: "create_lease"
    sandbox_lease_account_id: "account-123"
    sandbox_lease_user_id: "user-456"
    sandbox_lease_duration: 3600
    sandbox_lease_purpose: "Development testing"
```

### Extend a Lease

```yaml
- name: Extend a lease
  include_role:
    name: aws-sandbox-api
  vars:
    sandbox_action: "extend_lease"
    sandbox_lease_id: "lease-789"
    sandbox_lease_extension: 1800  # 30 minutes
```

### Using the Custom Module

```yaml
- name: Direct API call using custom module
  sandbox_api:
    action: "create_account"
    api_url: "https://your-sandbox-api.amazonaws.com"
    auth_type: "api_key"
    auth_config:
      api_key: "your-api-key"
    resource_data:
      name: "test-account"
      email: "admin@example.com"
      budget_limit: 100
      duration: 7200
  register: account_result
```

### Complete Playbook Example

```yaml
---
- name: Sandbox API Operations
  hosts: localhost
  vars:
    sandbox_api:
      base_url: "https://your-sandbox-api.amazonaws.com"
      auth:
        type: "api_key"
        api_key: "{{ vault_sandbox_api_key }}"
    
  tasks:
    - name: Health check
      include_role:
        name: aws-sandbox-api
      vars:
        sandbox_action: "health_check"
    
    - name: List accounts
      include_role:
        name: aws-sandbox-api
      vars:
        sandbox_action: "list_accounts"
    
    - name: Create account
      include_role:
        name: aws-sandbox-api
      vars:
        sandbox_action: "create_account"
        sandbox_account_name: "my-test-account"
        sandbox_account_email: "test@example.com"
      when: create_account | default(false)
```

## Response Variables

The role sets the following variables based on API responses:

- `sandbox_accounts_list`: List of accounts (when listing accounts)
- `sandbox_account_details`: Account details (when getting account)
- `sandbox_account_created`: Created account details (when creating account)
- `sandbox_leases_list`: List of leases (when listing leases)
- `sandbox_lease_details`: Lease details (when getting lease)
- `sandbox_lease_created`: Created lease details (when creating lease)
- `sandbox_users_list`: List of users (when listing users)
- `sandbox_user_created`: Created user details (when creating user)
- `sandbox_global_config`: Global configuration (when getting config)
- `sandbox_metrics`: System metrics (when getting metrics)
- `sandbox_status`: System status (when getting status)

## Error Handling

The role includes comprehensive error handling:

- **Retry Logic**: Automatic retry for transient failures
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Circuit Breaker**: Fails fast when service is unavailable
- **Detailed Logging**: Comprehensive logging for troubleshooting
- **Graceful Degradation**: Continues operation when possible

## Security Considerations

- Store API keys and credentials using Ansible Vault
- Use IAM roles when possible for AWS authentication
- Enable SSL certificate verification in production
- Implement proper access controls for API endpoints
- Monitor API usage and implement alerting

## Testing

```bash
# Test health check
ansible-playbook test-playbook.yml --tags health

# Test account operations
ansible-playbook test-playbook.yml --tags accounts

# Test with debugging
ansible-playbook test-playbook.yml -e "sandbox_dev.debug=true"
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**: Verify API credentials and endpoint URL
2. **Timeout Errors**: Increase timeout values or check network connectivity
3. **Rate Limiting**: Reduce request frequency or implement backoff
4. **SSL Errors**: Verify certificate configuration or disable verification for testing

### Debug Mode

Enable debug mode for detailed logging:

```yaml
sandbox_dev:
  debug: true
  verbose: true
```

### Logging

Check role logs for detailed information:

```bash
tail -f /tmp/sandbox-api.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This role is licensed under the Apache-2.0 License. See LICENSE file for details.

## Support

For questions, issues, or contributions:

- GitHub Issues: [Create an issue](https://github.com/your-org/aws-sandbox-api-role/issues)
- Documentation: [Role Documentation](https://github.com/your-org/aws-sandbox-api-role/wiki)
- Email: support@example.com

## Changelog

### Version 1.0.0
- Initial release
- Support for all major API operations
- Custom Ansible module
- Comprehensive error handling
- Multiple authentication methods
- Detailed documentation and examples 