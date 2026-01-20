#!/usr/bin/env python3
"""
Resource Provisioner CLI

A command-line tool for provisioning resources across different environments.
Environment configuration is set via environment variables.
"""

import os
import sys
import click
from typing import Optional


def get_environment_config() -> dict:
    """Load environment configuration from environment variables."""
    return {
        "host": os.environ.get("PROVISIONER_HOST", "localhost"),
        "environment": os.environ.get("PROVISIONER_ENV", "development"),
        "api_key": os.environ.get("PROVISIONER_API_KEY"),
        "dry_run": os.environ.get("PROVISIONER_DRY_RUN", "false").lower() == "true",
    }


def display_config(config: dict) -> None:
    """Display the current environment configuration."""
    click.echo(click.style("\n📋 Environment Configuration:", fg="cyan", bold=True))
    click.echo(f"   Host:        {config['host']}")
    click.echo(f"   Environment: {click.style(config['environment'], fg='yellow', bold=True)}")
    click.echo(f"   API Key:     {'*' * 8 if config['api_key'] else click.style('NOT SET', fg='red')}")
    click.echo(f"   Dry Run:     {config['dry_run']}")
    click.echo()


def confirm_action(action: str, resource_type: str, resource_name: str, config: dict, force: bool) -> bool:
    """Prompt user for confirmation before making changes."""
    if force:
        return True

    env_color = {
        "production": "red",
        "staging": "yellow",
        "development": "green",
    }.get(config["environment"], "white")

    click.echo(click.style("⚠️  WARNING", fg="yellow", bold=True))
    click.echo(f"You are about to {click.style(action.upper(), fg='red', bold=True)} the following resource:")
    click.echo(f"   Type:        {resource_type}")
    click.echo(f"   Name:        {resource_name}")
    click.echo(f"   Environment: {click.style(config['environment'], fg=env_color, bold=True)}")
    click.echo(f"   Host:        {config['host']}")
    click.echo()

    return click.confirm(
        click.style("Are you sure you want to make these changes?", fg="yellow"),
        default=False
    )


@click.group()
@click.version_option(version="1.0.0", prog_name="provisioner")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Resource Provisioner CLI

    Provision resources across different environments. Configure the target
    environment using environment variables:

    \b
      PROVISIONER_HOST     - Target server host (default: localhost)
      PROVISIONER_ENV      - Environment name (default: development)
      PROVISIONER_API_KEY  - API key for authentication
      PROVISIONER_DRY_RUN  - Set to 'true' for dry-run mode
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = get_environment_config()


@cli.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Display current environment configuration."""
    display_config(ctx.obj["config"])


# =============================================================================
# CREATE Commands
# =============================================================================

@cli.group()
def create() -> None:
    """Create new resources."""
    pass


@create.command("server")
@click.argument("name")
@click.option("--size", "-s", type=click.Choice(["small", "medium", "large"]), default="small", help="Server size")
@click.option("--region", "-r", default="us-east-1", help="Deployment region")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def create_server(ctx: click.Context, name: str, size: str, region: str, force: bool) -> None:
    """Create a new server instance."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Resource Details:")
    click.echo(f"   Size:   {size}")
    click.echo(f"   Region: {region}")
    click.echo()

    if not confirm_action("create", "server", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n✅ Successfully created server '{name}'", fg="green", bold=True))
        click.echo(f"   Provisioned on {config['host']} ({config['environment']})")


@create.command("database")
@click.argument("name")
@click.option("--engine", "-e", type=click.Choice(["postgres", "mysql", "redis"]), default="postgres", help="Database engine")
@click.option("--storage", "-s", type=int, default=20, help="Storage size in GB")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def create_database(ctx: click.Context, name: str, engine: str, storage: int, force: bool) -> None:
    """Create a new database instance."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Resource Details:")
    click.echo(f"   Engine:  {engine}")
    click.echo(f"   Storage: {storage} GB")
    click.echo()

    if not confirm_action("create", "database", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n✅ Successfully created database '{name}'", fg="green", bold=True))
        click.echo(f"   Provisioned on {config['host']} ({config['environment']})")


@create.command("bucket")
@click.argument("name")
@click.option("--public/--private", default=False, help="Bucket visibility")
@click.option("--versioning/--no-versioning", default=True, help="Enable versioning")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def create_bucket(ctx: click.Context, name: str, public: bool, versioning: bool, force: bool) -> None:
    """Create a new storage bucket."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Resource Details:")
    click.echo(f"   Visibility:  {'public' if public else 'private'}")
    click.echo(f"   Versioning:  {'enabled' if versioning else 'disabled'}")
    click.echo()

    if not confirm_action("create", "bucket", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n✅ Successfully created bucket '{name}'", fg="green", bold=True))
        click.echo(f"   Provisioned on {config['host']} ({config['environment']})")


# =============================================================================
# UPDATE Commands
# =============================================================================

@cli.group()
def update() -> None:
    """Update existing resources."""
    pass


@update.command("server")
@click.argument("name")
@click.option("--size", "-s", type=click.Choice(["small", "medium", "large"]), help="New server size")
@click.option("--restart/--no-restart", default=False, help="Restart server after update")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def update_server(ctx: click.Context, name: str, size: Optional[str], restart: bool, force: bool) -> None:
    """Update an existing server instance."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Update Details:")
    if size:
        click.echo(f"   New Size: {size}")
    click.echo(f"   Restart:  {'yes' if restart else 'no'}")
    click.echo()

    if not confirm_action("update", "server", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n✅ Successfully updated server '{name}'", fg="green", bold=True))
        click.echo(f"   Changes applied on {config['host']} ({config['environment']})")


@update.command("database")
@click.argument("name")
@click.option("--storage", "-s", type=int, help="New storage size in GB")
@click.option("--backup/--no-backup", default=True, help="Create backup before update")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def update_database(ctx: click.Context, name: str, storage: Optional[int], backup: bool, force: bool) -> None:
    """Update an existing database instance."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Update Details:")
    if storage:
        click.echo(f"   New Storage: {storage} GB")
    click.echo(f"   Backup:      {'yes' if backup else 'no'}")
    click.echo()

    if not confirm_action("update", "database", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n✅ Successfully updated database '{name}'", fg="green", bold=True))
        click.echo(f"   Changes applied on {config['host']} ({config['environment']})")


@update.command("bucket")
@click.argument("name")
@click.option("--public/--private", default=None, help="Change bucket visibility")
@click.option("--versioning/--no-versioning", default=None, help="Toggle versioning")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def update_bucket(ctx: click.Context, name: str, public: Optional[bool], versioning: Optional[bool], force: bool) -> None:
    """Update an existing storage bucket."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Update Details:")
    if public is not None:
        click.echo(f"   Visibility: {'public' if public else 'private'}")
    if versioning is not None:
        click.echo(f"   Versioning: {'enabled' if versioning else 'disabled'}")
    click.echo()

    if not confirm_action("update", "bucket", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n✅ Successfully updated bucket '{name}'", fg="green", bold=True))
        click.echo(f"   Changes applied on {config['host']} ({config['environment']})")


# =============================================================================
# DELETE Commands
# =============================================================================

@cli.group()
def delete() -> None:
    """Delete existing resources."""
    pass


@delete.command("server")
@click.argument("name")
@click.option("--keep-volumes/--delete-volumes", default=True, help="Keep attached volumes")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_server(ctx: click.Context, name: str, keep_volumes: bool, force: bool) -> None:
    """Delete a server instance."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Deletion Details:")
    click.echo(f"   Keep Volumes: {'yes' if keep_volumes else 'no'}")
    click.echo()

    click.echo(click.style("⚠️  This action is IRREVERSIBLE!", fg="red", bold=True))
    click.echo()

    if not confirm_action("delete", "server", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n🗑️  Successfully deleted server '{name}'", fg="green", bold=True))
        click.echo(f"   Removed from {config['host']} ({config['environment']})")


@delete.command("database")
@click.argument("name")
@click.option("--final-snapshot/--no-final-snapshot", default=True, help="Create final snapshot")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_database(ctx: click.Context, name: str, final_snapshot: bool, force: bool) -> None:
    """Delete a database instance."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Deletion Details:")
    click.echo(f"   Final Snapshot: {'yes' if final_snapshot else 'no'}")
    click.echo()

    click.echo(click.style("⚠️  This action is IRREVERSIBLE!", fg="red", bold=True))
    click.echo()

    if not confirm_action("delete", "database", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n🗑️  Successfully deleted database '{name}'", fg="green", bold=True))
        click.echo(f"   Removed from {config['host']} ({config['environment']})")


@delete.command("bucket")
@click.argument("name")
@click.option("--empty-first/--fail-if-not-empty", default=False, help="Empty bucket before deletion")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_bucket(ctx: click.Context, name: str, empty_first: bool, force: bool) -> None:
    """Delete a storage bucket."""
    config = ctx.obj["config"]
    display_config(config)

    click.echo(f"📦 Deletion Details:")
    click.echo(f"   Empty First: {'yes' if empty_first else 'no'}")
    click.echo()

    click.echo(click.style("⚠️  This action is IRREVERSIBLE!", fg="red", bold=True))
    click.echo()

    if not confirm_action("delete", "bucket", name, config, force):
        click.echo(click.style("❌ Operation cancelled.", fg="red"))
        sys.exit(1)

    if config["dry_run"]:
        click.echo(click.style("\n🔍 DRY RUN - No changes made", fg="cyan"))
    else:
        click.echo(click.style(f"\n🗑️  Successfully deleted bucket '{name}'", fg="green", bold=True))
        click.echo(f"   Removed from {config['host']} ({config['environment']})")


if __name__ == "__main__":
    cli()
