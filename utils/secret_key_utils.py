import secrets
import base64
from pathlib import Path
import os
from dotenv import load_dotenv


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key.
    Args:
        length: Length of the raw bytes (final base64 string will be longer)
    Returns:
        str: Base64 encoded secret key
    """
    # Generate random bytes
    raw_key = secrets.token_bytes(length)
    # Convert to base64 for storage/usage
    encoded_key = base64.b64encode(raw_key).decode('utf-8')
    return encoded_key


def save_secret_key_to_env(key: str, env_path: str = "../.env") -> None:
    """
    Save the secret key to a .env file.
    Will not overwrite existing secret key unless force=True.
    """
    env_path = Path(env_path)

    # Load existing env vars
    load_dotenv(env_path if env_path.exists() else None)

    # Check if secret key already exists
    if os.getenv("SECRET_KEY"):
        print("Warning: SECRET_KEY already exists in .env file")
        return

    # Create or append to .env file
    mode = 'a' if env_path.exists() else 'w'
    with open(env_path, mode) as f:
        f.write(f"\nSECRET_KEY='{key}'\n")

    print(f"Secret key has been saved to {env_path}")


def main():
    """Generate and save a new secret key."""
    # Generate the key
    secret_key = generate_secret_key()

    # Save to .env file
    save_secret_key_to_env(secret_key)

    print("\nGenerated secret key (keep this safe!):")
    print(secret_key)
    print("\nThis key has been saved to your .env file.")
    print("Make sure to never commit your .env file to version control!")


if __name__ == "__main__":
    main()
