"""
Azure Key Vault client wrapper for simplified secret management.

Usage:
    from keyvault import KeyVault
    
    kv = KeyVault("my-vault-name")
    secret = kv.get("my-secret")
    all_keys = kv.list_keys()
"""

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError


class KeyVault:
    """A wrapper class for Azure Key Vault operations."""
    
    def __init__(
        self,
        vault_name: str,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        """
        Initialize the KeyVault client.
        
        Args:
            vault_name: Name of the Azure Key Vault (not the full URL)
            tenant_id: Azure AD tenant ID (optional, for service principal auth)
            client_id: Service principal client ID (optional)
            client_secret: Service principal client secret (optional)
        
        If tenant_id, client_id, and client_secret are all provided, uses
        service principal authentication. Otherwise, uses DefaultAzureCredential
        which tries multiple auth methods (env vars, managed identity, Azure CLI, etc.)
        """
        self.vault_url = f"https://{vault_name}.vault.azure.net"
        
        if all([tenant_id, client_id, client_secret]):
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        else:
            credential = DefaultAzureCredential()
        
        self._client = SecretClient(vault_url=self.vault_url, credential=credential)
    
    def get(self, name: str, version: str | None = None) -> str | None:
        """
        Get a secret value by name.
        
        Args:
            name: Name of the secret
            version: Specific version to retrieve (optional, defaults to latest)
        
        Returns:
            The secret value as a string, or None if not found
        
        Raises:
            HttpResponseError: If there's an API error other than not found
        """
        try:
            secret = self._client.get_secret(name, version=version)
            return secret.value
        except ResourceNotFoundError:
            return None
    
    def get_or_raise(self, name: str, version: str | None = None) -> str:
        """
        Get a secret value, raising an exception if not found.
        
        Args:
            name: Name of the secret
            version: Specific version to retrieve (optional)
        
        Returns:
            The secret value as a string
        
        Raises:
            KeyError: If the secret doesn't exist
        """
        value = self.get(name, version)
        if value is None:
            raise KeyError(f"Secret '{name}' not found in vault")
        return value
    
    def list_keys(self, include_disabled: bool = False) -> list[str]:
        """
        List all secret names in the vault.
        
        Args:
            include_disabled: If True, include disabled secrets
        
        Returns:
            List of secret names
        """
        secrets = self._client.list_properties_of_secrets()
        
        if include_disabled:
            return [s.name for s in secrets]
        else:
            return [s.name for s in secrets if s.enabled]
    
    def list_secrets(self, include_disabled: bool = False) -> dict[str, str]:
        """
        List all secrets with their values.
        
        Args:
            include_disabled: If True, include disabled secrets
        
        Returns:
            Dictionary mapping secret names to their values
        """
        keys = self.list_keys(include_disabled=include_disabled)
        return {key: self.get(key) for key in keys}
    
    def exists(self, name: str) -> bool:
        """Check if a secret exists in the vault."""
        return self.get(name) is not None
    
    def set(self, name: str, value: str, **kwargs) -> None:
        """
        Set a secret value.
        
        Args:
            name: Name of the secret
            value: Value to store
            **kwargs: Additional arguments passed to set_secret
                     (content_type, enabled, expires_on, not_before, tags)
        """
        self._client.set_secret(name, value, **kwargs)
    
    def delete(self, name: str, purge: bool = False) -> None:
        """
        Delete a secret.
        
        Args:
            name: Name of the secret to delete
            purge: If True, permanently purge (requires soft-delete enabled)
        """
        poller = self._client.begin_delete_secret(name)
        poller.wait()
        
        if purge:
            self._client.purge_deleted_secret(name)
    
    def __getitem__(self, name: str) -> str:
        """Allow dict-like access: kv['my-secret']"""
        return self.get_or_raise(name)
    
    def __contains__(self, name: str) -> bool:
        """Allow 'in' operator: 'my-secret' in kv"""
        return self.exists(name)


# Example usage
if __name__ == "__main__":
    import os
    
    # Using DefaultAzureCredential (env vars, managed identity, or Azure CLI)
    vault_name = os.getenv("AZURE_KEYVAULT_NAME", "my-vault")
    
    kv = KeyVault(vault_name)
    
    # List all keys
    print("Available secrets:")
    for key in kv.list_keys():
        print(f"  - {key}")
    
    # Get a specific secret
    # secret_value = kv.get("my-secret")
    # or using dict-like syntax:
    # secret_value = kv["my-secret"]
