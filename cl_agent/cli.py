import click
from click_default_group import DefaultGroup
import json
import os
import subprocess
import sys
import tempfile
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
            app_data = os.environ.get("APPDATA") or str(
                Path.home() / "AppData" / "Roaming"
            )
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
        click.echo(
            f"Warning: Keys file at {keys_path} is corrupt. Using empty keys.", err=True
        )
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


def get_editor() -> str:
    """
    Get the user's preferred editor from environment variables.

    Returns:
        str: The editor command to use.
    """
    # Check environment variables in order of precedence
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")

    # Default to a sensible editor if none is specified
    if not editor:
        if os.name == "nt":  # Windows
            editor = "notepad"
        else:  # Unix-like
            # Try to find a common editor
            for ed in ["nano", "vim", "vi", "emacs"]:
                try:
                    if (
                        subprocess.run(
                            ["which", ed], capture_output=True, check=False
                        ).returncode
                        == 0
                    ):
                        editor = ed
                        break
                except Exception:
                    pass
            # Fall back to vi if nothing else found
            if not editor:
                editor = "vi"

    return editor


def launch_editor(initial_text="") -> str:
    """
    Launch an editor for the user to write text.

    Args:
        initial_text (str): Initial text to populate the editor with.

    Returns:
        str: The text content after editing.
    """
    editor = get_editor()

    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as tf:
        temp_path = tf.name
        # Write initial text if provided
        if initial_text:
            tf.write(initial_text)
        tf.flush()

    try:
        # Launch editor
        cmd = editor.split() + [temp_path]
        subprocess.run(cmd, check=True)

        # Read the edited content
        with open(temp_path, "r") as f:
            return f.read()
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except Exception:
            pass


@click.group(
    cls=DefaultGroup,
    default="run",
    default_if_no_args=True,
)
@click.version_option()
def cli():
    """A CLI agent that uses MCP"""
    pass


@cli.command()
@click.argument("prompt_text", required=False)
def run(prompt_text):
    """Send a prompt to the agent.

    Example:
        cla run "Hello, agent!"
        echo "Hello, agent!" | cla run
        cla run  # Opens an editor

    This command accepts input in multiple ways:
    - As a command-line argument
    - From stdin (pipe or redirect)
    - From a text editor if neither of the above is provided

    If both argument and stdin are provided, they are joined with a space.
    """
    stdin_text = ""

    # Check if we have data from stdin (but only if it's not a TTY, i.e., piped input)
    if not sys.stdin.isatty():
        stdin_text = sys.stdin.read().strip()

    combined_text = ""

    # Combine text from arguments and stdin if both are provided
    if prompt_text and stdin_text:
        combined_text = f"{prompt_text} {stdin_text}"
    elif prompt_text:
        combined_text = prompt_text
    elif stdin_text:
        combined_text = stdin_text
    else:
        # If no input, open editor
        combined_text = launch_editor().strip()

    if not combined_text:
        raise click.ClickException("No input provided")

    # Simple echo implementation for now
    click.echo(f"Prompt: {combined_text}")


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
