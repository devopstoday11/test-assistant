#!/usr/bin/env python3
"""Comprehensive unit tests for test-assistant."""
import unittest
import tempfile
import shutil
from pathlib import Path
import time
import yaml

from config_model import TestAssistantConfig
from file_handler import FileHandler
from claude_runner import ClaudeCodeRunner


class TestConfigModel(unittest.TestCase):
    """Test configuration model."""

    def setUp(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.yaml"

    def tearDown(self):
        """Cleanup test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_config(self):
        """Test loading valid configuration."""
        config_data = {
            "watch_path": self.temp_dir,
            "claude_prompt": "Test prompt",
            "file_extensions": [".txt", ".py"]
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = TestAssistantConfig.from_yaml(str(self.config_path))
        # Use Path().resolve() for comparison to handle symlinks like /var -> /private/var on macOS
        self.assertEqual(Path(config.watch_path).resolve(), Path(self.temp_dir).resolve())
        self.assertEqual(config.claude_prompt, "Test prompt")
        self.assertEqual(config.file_extensions, [".txt", ".py"])

    def test_invalid_watch_path(self):
        """Test that invalid watch path raises error."""
        config_data = {
            "watch_path": "/nonexistent/path",
            "claude_prompt": "Test prompt"
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        with self.assertRaises(ValueError):
            TestAssistantConfig.from_yaml(str(self.config_path))

    def test_extension_normalization(self):
        """Test that file extensions are normalized with dots."""
        config_data = {
            "watch_path": self.temp_dir,
            "claude_prompt": "Test",
            "file_extensions": ["txt", ".py", "md"]  # Mixed with/without dots
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = TestAssistantConfig.from_yaml(str(self.config_path))
        self.assertEqual(config.file_extensions, [".txt", ".py", ".md"])

    def test_default_values(self):
        """Test that default values are set correctly."""
        config_data = {
            "watch_path": self.temp_dir,
            "claude_prompt": "Test"
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = TestAssistantConfig.from_yaml(str(self.config_path))
        self.assertFalse(config.dry_run)
        self.assertEqual(config.timestamp_format, "mmddyy-HH-MM-SS-AMPM")
        self.assertFalse(config.process_existing_files)
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.file_stability_timeout, 5.0)

    def test_invalid_timestamp_format(self):
        """Test that invalid timestamp format raises error."""
        config_data = {
            "watch_path": self.temp_dir,
            "claude_prompt": "Test",
            "timestamp_format": "invalid-format"
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        with self.assertRaises(ValueError):
            TestAssistantConfig.from_yaml(str(self.config_path))


class TestFileHandler(unittest.TestCase):
    """Test file handler."""

    def setUp(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = FileHandler(
            watch_dir=self.temp_dir,
            timestamp_format="mmddyy-HH-MM-SS-AMPM"
        )

    def tearDown(self):
        """Cleanup test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_timestamp_generation_with_separators(self):
        """Test timestamp generation with separators."""
        handler = FileHandler(
            watch_dir=self.temp_dir,
            timestamp_format="mmddyy-HH-MM-SS-AMPM"
        )
        timestamp = handler.generate_timestamp()
        # Should match format: 102325-10-07-50-AM
        parts = timestamp.split('-')
        self.assertEqual(len(parts), 5)  # mmddyy, HH, MM, SS, AMPM
        self.assertEqual(len(parts[0]), 6)  # mmddyy
        self.assertIn(parts[4], ['AM', 'PM'])

    def test_timestamp_generation_without_separators(self):
        """Test timestamp generation without separators."""
        handler = FileHandler(
            watch_dir=self.temp_dir,
            timestamp_format="mmddyy-HHMMSS-AMPM"
        )
        timestamp = handler.generate_timestamp()
        # Should match format: 102325-100750-AM
        parts = timestamp.split('-')
        self.assertEqual(len(parts), 3)  # mmddyy, HHMMSS, AMPM
        self.assertEqual(len(parts[0]), 6)  # mmddyy
        self.assertEqual(len(parts[1]), 6)  # HHMMSS

    def test_find_latest_file(self):
        """Test finding file with -latest suffix."""
        # Create test files
        test_file1 = Path(self.temp_dir) / "102325-10-00-00-AM.txt"
        test_file2 = Path(self.temp_dir) / "102325-11-00-00-AM-latest.txt"

        test_file1.touch()
        test_file2.touch()

        latest = self.handler.find_latest_file()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.name, "102325-11-00-00-AM-latest.txt")

    def test_find_latest_file_none(self):
        """Test finding latest file when none exists."""
        latest = self.handler.find_latest_file()
        self.assertIsNone(latest)

    def test_remove_latest_suffix(self):
        """Test removing -latest suffix from file."""
        test_file = Path(self.temp_dir) / "102325-10-00-00-AM-latest.txt"
        test_file.touch()

        new_path = self.handler.remove_latest_suffix(test_file)
        self.assertEqual(new_path.name, "102325-10-00-00-AM.txt")
        self.assertTrue(new_path.exists())
        self.assertFalse(test_file.exists())

    def test_rename_to_latest(self):
        """Test renaming file with timestamp-latest format."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        new_path = self.handler.rename_to_latest(test_file)
        self.assertTrue("-latest.txt" in new_path.name)
        self.assertTrue(new_path.exists())
        self.assertFalse(test_file.exists())

    def test_process_new_file(self):
        """Test complete file processing workflow."""
        # Create existing latest file
        existing_latest = Path(self.temp_dir) / "102325-10-00-00-AM-latest.txt"
        existing_latest.write_text("old content")

        # Create new file
        new_file = Path(self.temp_dir) / "new.txt"
        new_file.write_text("new content")

        # Process new file
        result_path = self.handler.process_new_file(new_file)

        # Check that old file no longer has -latest
        old_file = Path(self.temp_dir) / "102325-10-00-00-AM.txt"
        self.assertTrue(old_file.exists())
        self.assertFalse(existing_latest.exists())

        # Check that new file has -latest
        self.assertTrue("-latest.txt" in result_path.name)
        self.assertTrue(result_path.exists())

    def test_file_stability_check(self):
        """Test file stability checking."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("initial content")

        handler = FileHandler(
            watch_dir=self.temp_dir,
            stability_timeout=2.0,
            stability_check_interval=0.1
        )

        # File should be stable immediately
        is_stable = handler.wait_for_file_stability(test_file)
        self.assertTrue(is_stable)

    def test_file_stability_check_disappears(self):
        """Test stability check when file disappears."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("content")

        handler = FileHandler(
            watch_dir=self.temp_dir,
            stability_timeout=2.0,
            stability_check_interval=0.1
        )

        # Delete file immediately to simulate disappearance
        test_file.unlink()

        # File should not be stable if it doesn't exist
        is_stable = handler.wait_for_file_stability(test_file)
        self.assertFalse(is_stable)


class TestClaudeRunner(unittest.TestCase):
    """Test Claude CLI runner."""

    def test_dry_run_mode(self):
        """Test that dry run mode skips actual execution."""
        runner = ClaudeCodeRunner(
            prompt_template="Test prompt",
            dry_run=True
        )

        temp_file = Path(tempfile.mktemp(suffix=".txt"))
        temp_file.write_text("test content")

        try:
            result = runner.run_claude_code(temp_file)
            self.assertIn("DRY RUN", result)
        finally:
            temp_file.unlink()

    def test_prompt_construction(self):
        """Test that prompt is constructed correctly."""
        runner = ClaudeCodeRunner(
            prompt_template="Analyze this:",
            dry_run=True  # Use dry run to avoid actual execution
        )

        # The prompt_template is stored
        self.assertEqual(runner.prompt_template, "Analyze this:")


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def setUp(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Cleanup test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_to_file_handler(self):
        """Test creating file handler from config."""
        config_path = Path(self.temp_dir) / "config.yaml"
        config_data = {
            "watch_path": self.temp_dir,
            "claude_prompt": "Test",
            "timestamp_format": "mmddyy-HHMMSS-AMPM",
            "file_stability_timeout": 3.0
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = TestAssistantConfig.from_yaml(str(config_path))
        handler = FileHandler(
            watch_dir=config.watch_path,
            timestamp_format=config.timestamp_format,
            stability_timeout=config.file_stability_timeout
        )

        self.assertEqual(handler.timestamp_format, "mmddyy-HHMMSS-AMPM")
        self.assertEqual(handler.stability_timeout, 3.0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigModel))
    suite.addTests(loader.loadTestsFromTestCase(TestFileHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestClaudeRunner))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
