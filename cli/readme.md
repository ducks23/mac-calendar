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
