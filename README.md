# Test-Assistant

A Python-based file watching service that automatically renames files with timestamps and triggers Claude Code CLI for analysis.

## Features

- 🔍 **File Watching**: Continuously monitors a directory for new files
- ⏰ **Smart Renaming**: Automatically renames files with `timestamp-latest` format
- 🔄 **Latest File Management**: Only the newest file has the `-latest` suffix
- 🤖 **Claude Code Integration**: Automatically triggers Claude Code CLI analysis
- ⚙️ **Configuration-Driven**: YAML-based configuration with Pydantic validation
- 📝 **Logging**: Comprehensive logging to both file and console

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Code CLI (install separately)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the tool by editing `config.yaml`:
```yaml
watch_path: "/path/to/watch"
claude_prompt: "Analyze this file and provide insights:"
file_extensions:
  - ".txt"
  - ".py"
  - ".md"
```

### Configuration Options

- **watch_path**: Directory to monitor for new files (must exist)
- **claude_prompt**: Prompt template to send to Claude Code CLI
- **file_extensions**: List of file extensions to watch (empty list `[]` = watch all files)

## Usage

### Start the Service

```bash
python main.py
```

Or specify a custom config file:
```bash
python main.py /path/to/custom-config.yaml
```

### Stop the Service

Press `Ctrl+C` in the terminal

## How It Works

1. **File Detection**: Service watches the configured directory
2. **File Processing**:
   - When a new file appears, finds any existing file with `-latest` suffix
   - Removes `-latest` from the old file
   - Renames new file with format: `mmddyy-HHMMSSAM/PM-latest`
3. **Claude Code Execution**:
   - Automatically triggers Claude Code CLI
   - Passes configured prompt + file path
   - Displays output in the terminal
4. **Continuous Operation**: Returns to watching for the next file

## File Naming Convention

### Timestamp Format
`mmddyy-HHMMSSAM/PM-latest`

Examples:
- `102225-023022PM-latest.txt` (October 22, 2025 at 2:30:22 PM)
- `102225-113045AM-latest.py` (October 22, 2025 at 11:30:45 AM)

### Naming Workflow

**Initial State**: Empty directory

**File 1 arrives** (`test.txt`):
- Renamed to: `102225-023022PM-latest.txt`

**File 2 arrives** (`data.csv`):
- `102225-023022PM-latest.txt` → `102225-023022PM.txt` (removes `-latest`)
- `data.csv` → `102225-023115PM-latest.csv` (new file gets `-latest`)

## Project Structure

```
test-assistant/
├── main.py              # Entry point and service orchestration
├── config_model.py      # Pydantic configuration models
├── file_handler.py      # File renaming logic
├── claude_runner.py     # Claude Code CLI integration
├── event_handler.py     # Watchdog event handling
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── test-assistant.log      # Log file (generated)
└── README.md           # This file
```

## Logging

Logs are written to:
- Console (stdout)
- `test-assistant.log` file

Log format includes timestamp, logger name, level, and message.

## Error Handling

- Configuration validation on startup
- Graceful handling of file operations
- Claude Code CLI timeout (5 minutes)
- Comprehensive error logging

## Example Session

```
================================================================================
🚀 TEST-ASSISTANT SERVICE STARTED
================================================================================
📂 Watching directory: /home/user/watch-folder
🤖 Claude prompt: Analyze this file and provide insights:
📄 Watching extensions: .txt, .py, .md
================================================================================

👀 Waiting for new files...
Press Ctrl+C to stop the service

📁 NEW FILE DETECTED: test.txt
✅ FILE RENAMED: 102225-023022PM-latest.txt

================================================================================
🤖 TRIGGERING CLAUDE CODE CLI
================================================================================
File: /home/user/watch-folder/102225-023022PM-latest.txt
Prompt: Analyze this file and provide insights: /home/user/watch-folder/102225-023022PM-latest.txt
================================================================================

CLAUDE CODE OUTPUT:
--------------------------------------------------------------------------------
[Claude Code CLI output appears here]
--------------------------------------------------------------------------------

================================================================================
✅ CLAUDE CODE EXECUTION COMPLETED
================================================================================

👀 Watching for next file...
```

## Troubleshooting

### Claude Code CLI Not Found

If you see:
```
⚠️  WARNING: claude-code CLI is not available!
```

Ensure:
1. Claude Code CLI is installed
2. It's in your system PATH
3. You can run `claude-code --version` successfully

### Watch Directory Not Found

Ensure the `watch_path` in config.yaml:
- Points to an existing directory
- Has proper read/write permissions
- Uses absolute path or path relative to where you run the script

### Files Not Being Detected

Check:
1. `file_extensions` in config.yaml matches your files
2. Files are being created (not moved) into the directory
3. Check `test-assistant.log` for detailed error messages

## License

MIT License - Feel free to use and modify as needed.
