# Resource Provisioner CLI

A command-line tool for provisioning resources across different environments using Python Click.

## Installation

```bash
pip install -e .
```

Or run directly:

```bash
python provisioner.py --help
```

## Configuration

Set environment variables to configure the target environment:

| Variable              | Description                    | Default       |
| --------------------- | ------------------------------ | ------------- |
| `PROVISIONER_HOST`    | Target server host             | `localhost`   |
| `PROVISIONER_ENV`     | Environment name               | `development` |
| `PROVISIONER_API_KEY` | API key for authentication     | (none)        |
| `PROVISIONER_DRY_RUN` | Set to `true` for dry-run mode | `false`       |

### Example Configuration

```bash
# Development (default)
export PROVISIONER_HOST="dev.example.com"
export PROVISIONER_ENV="development"

# Staging
export PROVISIONER_HOST="staging.example.com"
export PROVISIONER_ENV="staging"

# Production
export PROVISIONER_HOST="prod.example.com"
export PROVISIONER_ENV="production"
export PROVISIONER_API_KEY="your-api-key"
```

## Usage

### View Current Configuration

```bash
provisioner config
```

### Create Resources

```bash
# Create a server
provisioner create server my-web-server --size medium --region us-west-2

# Create a database
provisioner create database my-postgres --engine postgres --storage 50

# Create a storage bucket
provisioner create bucket my-assets --public --versioning
```

### Update Resources

```bash
# Update server size
provisioner update server my-web-server --size large --restart

# Increase database storage
provisioner update database my-postgres --storage 100 --backup

# Change bucket visibility
provisioner update bucket my-assets --private
```

### Delete Resources

```bash
# Delete a server (keeps volumes by default)
provisioner delete server my-web-server

# Delete a database with final snapshot
provisioner delete database my-postgres --final-snapshot

# Delete a bucket (must be empty by default)
provisioner delete bucket my-assets --empty-first
```

### Flags

All commands support:

- `--force` / `-f`: Skip the confirmation prompt
- `--help`: Show command help

## Confirmation Prompts

All create, update, and delete operations require confirmation. The prompt shows:

- The action being performed
- Resource type and name
- Target environment (color-coded by risk level)
- Target host

Use `--force` to skip confirmation (useful for automation).

## Dry Run Mode

Enable dry-run mode to preview changes without applying them:

```bash
export PROVISIONER_DRY_RUN=true
provisioner create server test-server --force
```

## Examples

### Production Deployment with Confirmation

```bash
$ export PROVISIONER_ENV=production
$ export PROVISIONER_HOST=prod.example.com

$ provisioner create server api-server --size large

📋 Environment Configuration:
   Host:        prod.example.com
   Environment: production
   API Key:     ********
   Dry Run:     False

📦 Resource Details:
   Size:   large
   Region: us-east-1

⚠️  WARNING
You are about to CREATE the following resource:
   Type:        server
   Name:        api-server
   Environment: production
   Host:        prod.example.com

Are you sure you want to make these changes? [y/N]: y

✅ Successfully created server 'api-server'
   Provisioned on prod.example.com (production)
```

### Automated CI/CD Pipeline

```bash
# Skip confirmation in automation
PROVISIONER_ENV=staging \
PROVISIONER_HOST=staging.example.com \
provisioner update server api-server --size medium --force
```
