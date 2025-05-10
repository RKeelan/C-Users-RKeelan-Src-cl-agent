# cl-agent

[![PyPI](https://img.shields.io/pypi/v/cl-agent.svg)](https://pypi.org/project/cl-agent/)
[![Changelog](https://img.shields.io/github/v/release/RKeelan/cl-agent?include_prereleases&label=changelog)](https://github.com/RKeelan/cl-agent/releases)
[![Tests](https://github.com/RKeelan/cl-agent/actions/workflows/test.yml/badge.svg)](https://github.com/RKeelan/cl-agent/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/RKeelan/cl-agent/blob/master/LICENSE)

A CLI agent that uses MCP

## Installation

Install this tool using `pip`:
```bash
pip install cl-agent
```
## Usage

For help, run:
```bash
cla --help
```
You can also use:
```bash
python -m cla --help
```

### Managing API Keys

The `cla keys` subcommand allows you to securely store and manage API keys:

```bash
# Set a key (will prompt for value)
cla keys set openai

# Set a key with a value directly
cla keys set openai --value sk-your-key-here

# Retrieve a stored key
cla keys get openai

# Use a key in another command
export OPENAI_API_KEY="$(cla keys get openai)"

# List all stored keys (without showing values)
cla keys list

# Show the path to the keys.json file
cla keys path
```

Keys are stored in a JSON file with secure permissions (readable only by the current user). The file location varies by platform:
- Linux: `~/.config/cl-agent/keys.json`
- macOS: `~/Library/Application Support/cl-agent/keys.json`
- Windows: `%APPDATA%\cl-agent\keys.json`

You can customize the storage location by setting the `CLA_USER_PATH` environment variable.

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd cl-agent
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
