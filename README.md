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
