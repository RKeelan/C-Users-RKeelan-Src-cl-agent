import click
import json
import os
from pathlib import Path
import stat


def user_dir() -> Path:
    """
    Get the user directory for storing cl-agent data.
    
    Returns:
        Path: The directory path for storing user data.
    """
    if os.environ.get("CLA_USER_PATH"):
        path = Path(os.environ["CLA_USER_PATH"])
    else:
        # Handle different platforms
        if os.name == "nt":  # Windows
            app_data = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
            path = Path(app_data) / "cl-agent"
        else:  # macOS, Linux, etc.
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config_home:
                path = Path(xdg_config_home) / "cl-agent"
            else:
                # macOS: ~/Library/Application Support/cl-agent
                # Linux: ~/.config/cl-agent
                if Path("/Applications").exists():  # Heuristic for macOS
                    path = Path.home() / "Library" / "Application Support" / "cl-agent"
                else:
                    path = Path.home() / ".config" / "cl-agent"
    
    # Ensure the directory exists
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_keys_path() -> Path:
    """
    Get the path to the keys.json file.
    
    Returns:
        Path: The path to the keys.json file.
    """
    return user_dir() / "keys.json"


def load_keys() -> dict:
    """
    Load keys from the keys.json file.
    
    Returns:
        dict: The loaded keys or an empty dict if the file doesn't exist.
    """
    keys_path = get_keys_path()
    if not keys_path.exists():
        return {}
    
    try:
        return json.loads(keys_path.read_text())
    except json.JSONDecodeError:
        # Handle corrupt file
        click.echo(f"Warning: Keys file at {keys_path} is corrupt. Using empty keys.", err=True)
        return {}


def save_keys(keys: dict) -> None:
    """
    Save keys to the keys.json file.
    
    Args:
        keys (dict): The keys to save.
    """
    keys_path = get_keys_path()
    
    # Create file with secure permissions (600)
    with open(keys_path, "w") as f:
        json.dump(keys, f, indent=2)
    
    # Set permissions to user read/write only
    if os.name != "nt":  # Skip on Windows
        os.chmod(keys_path, stat.S_IRUSR | stat.S_IWUSR)


@click.group()
@click.version_option()
def cli():
    "A CLI agent that uses MCP"
    pass


@cli.group(name="keys")
def keys():
    """Manage API keys for services used by cl-agent."""
    pass


@keys.command(name="set")
@click.argument("name")
@click.option("--value", prompt="Enter key", hide_input=True, help="Value to set")
def keys_set(name, value):
    """Set an API key with the given name.
    
    Example:
        cla keys set openai
    
    This will prompt for the key value or you can provide it with --value.
    The key will be stored securely in your user directory.
    """
    keys = load_keys()
    keys[name] = value
    save_keys(keys)
    click.echo(f"Key '{name}' has been set")


@keys.command(name="get")
@click.argument("name")
def keys_get(name):
    """Get the value of a stored API key.
    
    Example:
        cla keys get openai
        export OPENAI_API_KEY="$(cla keys get openai)"
    
    This outputs the key value for the given name.
    """
    keys = load_keys()
    try:
        click.echo(keys[name])
    except KeyError:
        raise click.ClickException(f"No key found with name '{name}'")


@keys.command(name="list")
def keys_list():
    """List all stored API key names.
    
    Example:
        cla keys list
    
    This lists the names of all stored keys without showing their values.
    """
    keys = load_keys()
    if not keys:
        click.echo("No keys found")
        return
    
    for key in sorted(keys.keys()):
        click.echo(key)


@keys.command(name="path")
def keys_path_command():
    """Show the path to the keys.json file.
    
    Example:
        cla keys path
    
    This outputs the full path to the file where keys are stored.
    """
    click.echo(get_keys_path())
