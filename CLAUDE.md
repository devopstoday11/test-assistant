# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Test-assistant is a Python-based file watching service that automatically renames files with timestamps and triggers Claude CLI for analysis. It uses the watchdog library to monitor a directory, applies a configurable timestamp-based naming convention, and integrates with Claude CLI (command: `claude -p`) to automatically analyze newly created files.

**Key Features:**
- Configurable timestamp formats with separators
- Dry-run mode for testing without Claude execution
- Queue-based concurrent file handling
- File size stability checking (waits for files to finish writing)
- Process existing files on startup (optional)
- Configurable logging levels (DEBUG, INFO, WARNING, ERROR)
- Graceful handling of watch directory deletion

## Common Commands

### Development and Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script (creates watch directory, configures config.yaml)
python setup.py

# Run comprehensive unit tests (17 tests covering all components)
python test_cheat_tool.py

# Start the service (uses config.yaml by default)
python main.py

# Start with custom config
python main.py /path/to/custom-config.yaml

# Run manual integration test (creates test files in watch directory)
python test_tool.py
```

### Testing Dry-Run Mode

```bash
# Test file renaming without triggering Claude CLI
# Edit config.yaml and set: dry_run: true
python main.py
```

### Testing Individual Components

```python
# Test configuration loading with new options
from config_model import TestAssistantConfig
config = TestAssistantConfig.from_yaml("config.yaml")
print(f"Dry run: {config.dry_run}")
print(f"Timestamp format: {config.timestamp_format}")

# Test file handler with configurable timestamp
from file_handler import FileHandler
handler = FileHandler(
    watch_dir="/path/to/watch",
    timestamp_format="mmddyy-HH-MM-SS-AMPM",
    stability_timeout=5.0
)
timestamp = handler.generate_timestamp()  # Returns with separators: 102325-10-07-50-AM

# Test Claude runner with dry-run mode
from claude_runner import ClaudeCodeRunner
runner = ClaudeCodeRunner("Analyze this file:", dry_run=True)
runner.check_claude_code_available()  # Check if claude CLI is installed
```

## Architecture

### Core Components and Data Flow

1. **main.py (TestAssistantService)** - Service orchestration
   - Loads configuration from YAML using Pydantic validation
   - Sets up logging with configurable levels
   - Initializes all components with configuration parameters
   - Optionally processes existing files on startup
   - Monitors watch directory existence during runtime
   - Manages service lifecycle with graceful shutdown

2. **config_model.py (TestAssistantConfig)** - Configuration management
   - Pydantic models for type-safe configuration with validation
   - **Required fields:** watch_path, claude_prompt
   - **Optional fields with defaults:**
     - `dry_run` (bool): Skip Claude execution
     - `timestamp_format` (str): Customizable format with validation
     - `process_existing_files` (bool): Process files on startup
     - `log_level` (str): DEBUG, INFO, WARNING, or ERROR
     - `file_stability_timeout` (float): Max wait for file to stabilize
     - `file_stability_check_interval` (float): Check interval
   - Validates watch_path exists and is a directory
   - Auto-formats file extensions to include leading dot
   - Validates timestamp format against allowed formats

3. **event_handler.py (TestAssistantEventHandler)** - Watchdog event processor
   - Listens for FileCreatedEvent on watch directory
   - Filters files by extension (if configured)
   - **Queue-based concurrent handling:** Uses `queue.Queue()` with worker thread
   - Files are added to queue immediately, processed sequentially
   - Worker thread runs `_process_file()` for each queued file
   - Graceful shutdown with `shutdown()` method
   - Orchestrates file renaming and Claude CLI execution

4. **file_handler.py (FileHandler)** - File renaming logic
   - Implements `-latest` suffix management pattern
   - **Configurable timestamp formats:**
     - `mmddyy-HH-MM-SS-AMPM` → `102325-10-07-50-AM` (default, with separators)
     - `mmddyy-HHMMSS-AMPM` → `102325-100750-AM` (no separators)
     - `mmddyy-HH:MM:SS-AMPM` → `102325-10:07:50-AM` (colon separators)
   - **File stability checking:** Waits for file size to stop changing
   - `process_new_file()` workflow:
     - Find existing file with `-latest` suffix
     - Remove `-latest` from old file
     - Rename new file with timestamp + `-latest` suffix

5. **claude_runner.py (ClaudeCodeRunner)** - Claude CLI integration
   - Executes `claude -p` subprocess with prompt + file path
   - **Dry-run mode:** Skips execution when enabled
   - 5 minute timeout for CLI execution
   - Captures and displays stdout/stderr

### File Renaming Workflow

The tool maintains only ONE file with the `-latest` suffix at any time:

```
1. Initial state: empty directory
2. File "test.txt" created → renamed to "102225-023022PM-latest.txt"
3. File "data.csv" created →
   - "102225-023022PM-latest.txt" → "102225-023022PM.txt" (remove -latest)
   - "data.csv" → "102225-023115PM-latest.csv" (add -latest to new file)
```

### Configuration Structure

config.yaml contains:
- **watch_path**: Directory to monitor (validated to exist)
- **claude_prompt**: Prompt template sent to Claude Code CLI
- **file_extensions**: Optional list to filter by extension (empty = all files)

Extensions are normalized to include leading dot during validation.

## Key Implementation Details

### Timestamp Format (Configurable)
- **Three supported formats** (configured in config.yaml):
  - `mmddyy-HH-MM-SS-AMPM` → `102325-10-07-50-AM` (default)
  - `mmddyy-HHMMSS-AMPM` → `102325-100750-AM`
  - `mmddyy-HH:MM:SS-AMPM` → `102325-10:07:50-AM`
- Generated in `FileHandler.generate_timestamp()` using `datetime.now()`
- 12-hour format with AM/PM suffix
- Format validated during configuration loading

### Concurrency Handling (Queue-Based)
- **Queue-based processing** replaces boolean flag approach
- Files added to `queue.Queue()` immediately on detection
- Dedicated worker thread processes files sequentially
- Multiple files can arrive simultaneously without conflicts
- Graceful shutdown: stops queue processing and joins worker thread

### File Stability Checking
- **Replaces fixed 0.5s delay** with adaptive checking
- Polls file size at configured interval (default: 0.1s)
- Waits until size stops changing (file fully written)
- Maximum wait time: configurable timeout (default: 5.0s)
- Returns False if file disappears during check
- Implemented in `FileHandler.wait_for_file_stability()`

### Error Handling
- Configuration validation on startup (fails fast if watch_path invalid)
- **Watch directory monitoring:** Checks if directory still exists during runtime
- Claude CLI availability check with warning (service continues even if CLI missing)
- **Dry-run mode:** Skips CLI execution for testing
- Comprehensive logging to both console and `test-assistant.log`
- Graceful shutdown on Ctrl+C or directory deletion

### Subprocess Execution
- Claude CLI called via `subprocess.run()` with 5 minute timeout
- **Command format:** `claude -p "prompt template /path/to/file"`
- Uses `-p` flag for non-interactive (print) mode
- Both stdout and stderr captured and displayed
- Skipped entirely in dry-run mode

### Configuration Options
All optional settings have sensible defaults:
- `dry_run: false` - Test without Claude execution
- `timestamp_format: "mmddyy-HH-MM-SS-AMPM"` - Format with separators
- `process_existing_files: false` - Don't process existing files on startup
- `log_level: "INFO"` - Normal verbosity
- `file_stability_timeout: 5.0` - Wait up to 5 seconds for file stability
- `file_stability_check_interval: 0.1` - Check every 100ms

## Security Best Practices

When modifying or adding code:
- Always run snyk_code_scan tool for new first-party code in Snyk-supported languages
- Fix any security issues found in newly introduced/modified code or dependencies
- Rescan after fixes to ensure issues resolved and no new issues introduced
- Repeat until no new issues found

## Dependencies

- **pydantic** (≥2.0.0): Configuration validation and models
- **PyYAML** (≥6.0): YAML configuration parsing
- **watchdog** (≥3.0.0): File system event monitoring

## Python Version

Requires Python 3.8 or higher (checked in setup.py).
