import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cl_agent.cli import cli, user_dir, get_keys_path, load_keys, save_keys


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


class TestKeysCommands:
    def setup_method(self):
        self.runner = CliRunner()
        # Create a patched user_dir for isolated testing
        self.test_dir_patcher = patch('cl_agent.cli.user_dir')
        self.mock_user_dir = self.test_dir_patcher.start()
        
    def teardown_method(self):
        self.test_dir_patcher.stop()
        
    def test_keys_set_and_get(self):
        with self.runner.isolated_filesystem() as fs:
            # Setup mocked user directory to point to our isolated filesystem
            test_dir = Path(fs) / "test_config"
            test_dir.mkdir()
            self.mock_user_dir.return_value = test_dir
            
            # Test setting a key
            result = self.runner.invoke(cli, ["keys", "set", "testkey"], input="mysecretvalue\n")
            assert result.exit_code == 0
            assert "Key 'testkey' has been set" in result.output
            
            # Verify the key was saved properly
            keys_path = test_dir / "keys.json"
            assert keys_path.exists()
            with open(keys_path) as f:
                keys = json.load(f)
                assert "testkey" in keys
                assert keys["testkey"] == "mysecretvalue"
            
            # Test getting the key
            result = self.runner.invoke(cli, ["keys", "get", "testkey"])
            assert result.exit_code == 0
            assert "mysecretvalue" in result.output.strip()
            
            # Test getting a non-existent key
            result = self.runner.invoke(cli, ["keys", "get", "nonexistent"])
            assert result.exit_code != 0
            assert "No key found with name 'nonexistent'" in result.output
    
    def test_keys_list(self):
        with self.runner.isolated_filesystem() as fs:
            # Setup mocked user directory to point to our isolated filesystem
            test_dir = Path(fs) / "test_config"
            test_dir.mkdir()
            self.mock_user_dir.return_value = test_dir
            
            # Test with no keys
            result = self.runner.invoke(cli, ["keys", "list"])
            assert result.exit_code == 0
            assert "No keys found" in result.output
            
            # Add some keys
            keys_path = test_dir / "keys.json"
            test_keys = {"api1": "value1", "api2": "value2", "zapi": "value3"}
            with open(keys_path, "w") as f:
                json.dump(test_keys, f)
            
            # Test keys are listed in alphabetical order
            result = self.runner.invoke(cli, ["keys", "list"])
            assert result.exit_code == 0
            assert "api1\napi2\nzapi" in result.output.strip()
    
    def test_keys_path(self):
        with self.runner.isolated_filesystem() as fs:
            # Setup mocked user directory to point to our isolated filesystem
            test_dir = Path(fs) / "test_config"
            test_dir.mkdir()
            self.mock_user_dir.return_value = test_dir
            
            result = self.runner.invoke(cli, ["keys", "path"])
            assert result.exit_code == 0
            assert str(test_dir / "keys.json") in result.output.strip()