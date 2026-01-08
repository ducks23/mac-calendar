#!/usr/bin/env python3
"""
Keycloak provisioning script for Calendar App.
Creates a realm, client, and roles (reader, writer, owner).
"""

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError
import os

# Configuration - adjust these or use environment variables
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
ADMIN_USERNAME = os.getenv("KEYCLOAK_ADMIN", "admin")
ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")

# Calendar app configuration
REALM_NAME = "calendar"
CLIENT_ID = "calendar-app"
CLIENT_ROLES = ["reader", "writer", "owner"]


def get_admin_client() -> KeycloakAdmin:
    """Create and return a KeycloakAdmin client connected to master realm."""
    return KeycloakAdmin(
        server_url=KEYCLOAK_URL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        realm_name="master",
        verify=True,
    )


def create_realm(admin: KeycloakAdmin, realm_name: str) -> None:
    """Create a new realm if it doesn't exist."""
    try:
        admin.get_realm(realm_name)
        print(f"Realm '{realm_name}' already exists")
    except KeycloakGetError:
        admin.create_realm(
            payload={
                "realm": realm_name,
                "enabled": True,
                "displayName": "Calendar Application",
                "registrationAllowed": False,
                "loginWithEmailAllowed": True,
                "duplicateEmailsAllowed": False,
                "resetPasswordAllowed": True,
                "editUsernameAllowed": False,
                "bruteForceProtected": True,
            },
            skip_exists=True,
        )
        print(f"Created realm '{realm_name}'")


def create_client(admin: KeycloakAdmin, client_id: str) -> str:
    """Create a client and return its internal ID."""
    # Check if client already exists
    clients = admin.get_clients()
    for client in clients:
        if client.get("clientId") == client_id:
            print(f"Client '{client_id}' already exists")
            return client["id"]

    # Create the client
    client_payload = {
        "clientId": client_id,
        "name": "Calendar Application",
        "description": "Calendar application client",
        "enabled": True,
        "publicClient": False,  # Confidential client
        "standardFlowEnabled": True,  # Authorization code flow
        "directAccessGrantsEnabled": True,  # Resource owner password credentials
        "serviceAccountsEnabled": True,  # For backend service calls
        "authorizationServicesEnabled": False,
        "protocol": "openid-connect",
        "redirectUris": [
            "http://localhost:3000/*",
            "http://localhost:8000/*",
        ],
        "webOrigins": [
            "http://localhost:3000",
            "http://localhost:8000",
        ],
        "attributes": {
            "access.token.lifespan": "300",  # 5 minutes
            "pkce.code.challenge.method": "S256",
        },
    }

    admin.create_client(client_payload)
    print(f"Created client '{client_id}'")

    # Get the internal client ID
    client_internal_id = admin.get_client_id(client_id)
    return client_internal_id


def create_client_roles(admin: KeycloakAdmin, client_internal_id: str, roles: list[str]) -> None:
    """Create client-specific roles."""
    existing_roles = admin.get_client_roles(client_internal_id)
    existing_role_names = {role["name"] for role in existing_roles}

    for role_name in roles:
        if role_name in existing_role_names:
            print(f"Role '{role_name}' already exists")
            continue

        role_payload = {
            "name": role_name,
            "description": f"Calendar {role_name} role",
            "composite": False,
            "clientRole": True,
        }
        admin.create_client_role(client_internal_id, role_payload, skip_exists=True)
        print(f"Created role '{role_name}'")


def get_client_secret(admin: KeycloakAdmin, client_internal_id: str) -> str:
    """Retrieve the client secret."""
    secret_data = admin.get_client_secrets(client_internal_id)
    return secret_data.get("value", "")


def main():
    print(f"Connecting to Keycloak at {KEYCLOAK_URL}...")

    # Connect to master realm
    admin = get_admin_client()
    print("Connected to Keycloak")

    # Create the realm
    create_realm(admin, REALM_NAME)

    # Switch to the new realm
    admin.change_current_realm(REALM_NAME)

    # Create the client
    client_internal_id = create_client(admin, CLIENT_ID)

    # Create client roles
    create_client_roles(admin, client_internal_id, CLIENT_ROLES)

    # Get client secret
    client_secret = get_client_secret(admin, client_internal_id)

    print("\n" + "=" * 50)
    print("Provisioning complete!")
    print("=" * 50)
    print(f"Realm:         {REALM_NAME}")
    print(f"Client ID:     {CLIENT_ID}")
    print(f"Client Secret: {client_secret}")
    print(f"Roles:         {', '.join(CLIENT_ROLES)}")
    print("\nKeycloak URLs:")
    print(f"  Realm:    {KEYCLOAK_URL}/realms/{REALM_NAME}")
    print(f"  Auth:     {KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/auth")
    print(f"  Token:    {KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token")
    print(f"  Userinfo: {KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/userinfo")


if __name__ == "__main__":
    main()



# Add this to your provisioning script or run separately
admin.create_user({
    "username": "testuser",
    "email": "test@example.com",
    "enabled": True,
    "credentials": [{"type": "password", "value": "testpass", "temporary": False}],
})

# Assign a role to the user
user_id = admin.get_user_id("testuser")
client_internal_id = admin.get_client_id("calendar-app")
role = admin.get_client_role(client_internal_id, "owner")
admin.assign_client_role(user_id, client_internal_id, [role])
