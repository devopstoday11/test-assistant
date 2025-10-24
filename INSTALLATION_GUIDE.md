# 🚀 Cheat-Tool - Complete Installation & Usage Guide

## 📦 What You've Got

A complete Python-based file watching service that:
- ✅ Monitors a directory for new files
- ✅ Automatically renames files with timestamp-latest format (12-hour AM/PM)
- ✅ Manages -latest suffix (only newest file has it)
- ✅ Triggers Claude Code CLI automatically
- ✅ Displays all output in the same terminal
- ✅ Runs continuously until you stop it

## 📂 Project Contents

```
test-assistant/
├── 📘 Documentation
│   ├── README.md              # Comprehensive documentation
│   ├── QUICKSTART.md          # Quick start guide
│   └── EXAMPLE_SESSION.md     # Example output walkthrough
│
├── 🐍 Core Application
│   ├── main.py               # Entry point - run this!
│   ├── config_model.py       # Pydantic configuration validation
│   ├── file_handler.py       # File renaming logic
│   ├── claude_runner.py      # Claude Code CLI integration
│   └── event_handler.py      # Watchdog event handling
│
├── ⚙️ Configuration
│   └── config.yaml           # Edit your settings here
│
├── 🛠️ Utilities
│   ├── setup.py             # Initial setup script
│   └── test_tool.py         # Test the installation
│
└── 📋 Dependencies
    ├── requirements.txt     # Python packages
    └── .gitignore          # Git ignore rules
```

## 🏃 Quick Start (3 Steps)

### Step 1: Setup
```bash
cd test-assistant
python setup.py
```

This automatically:
- Installs all required packages
- Creates watch directory at `~/test-assistant-watch`
- Updates config.yaml with the directory path
- Checks if Claude Code CLI is available

### Step 2: Run the Service
```bash
python main.py
```

You'll see:
```
================================================================================
🚀 CHEAT-TOOL SERVICE STARTED
================================================================================
📂 Watching directory: /home/user/test-assistant-watch
🤖 Claude prompt: Analyze this file and provide insights:
👀 Waiting for new files...
```

### Step 3: Test It
Open a new terminal and run:
```bash
cd test-assistant
python test_tool.py
```

Or manually create a test file:
```bash
echo "Hello World" > ~/test-assistant-watch/test.txt
```

Watch the first terminal - you'll see:
- ✅ File detection
- ✅ Renaming to timestamp format
- ✅ Claude Code execution
- ✅ Output display

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Directory to monitor (must exist)
watch_path: "/home/user/test-assistant-watch"

# Prompt sent to Claude Code CLI
claude_prompt: "Analyze this file and provide insights:"

# File types to watch (empty list = all files)
file_extensions:
  - ".txt"
  - ".py"
  - ".md"
```

### Common Configurations

**Watch all file types:**
```yaml
file_extensions: []
```

**Watch specific types:**
```yaml
file_extensions: [".txt", ".py", ".js", ".md"]
```

**Custom directory:**
```yaml
watch_path: "/path/to/your/directory"
```

**Custom Claude prompt:**
```yaml
claude_prompt: "Review this code for bugs and security issues:"
```

## 📝 File Naming Convention

### Format
`mmddyy-HHMMSSAM/PM-latest`

### Examples
- `102225-023022PM-latest.txt` → Oct 22, 2025 at 2:30:22 PM
- `102225-113045AM-latest.py` → Oct 22, 2025 at 11:30:45 AM
- `120125-061530PM-latest.md` → Dec 1, 2025 at 6:15:30 PM

### How It Works

**Scenario 1: First file**
```
Directory: empty
Add: test.txt
Result: 102225-023022PM-latest.txt
```

**Scenario 2: Second file arrives**
```
Directory: 102225-023022PM-latest.txt
Add: data.csv
Result: 
  - 102225-023022PM.txt (removed -latest)
  - 102225-023115PM-latest.csv (new file)
```

**Scenario 3: Third file arrives**
```
Directory: 
  - 102225-023022PM.txt
  - 102225-023115PM-latest.csv
Add: notes.md
Result:
  - 102225-023022PM.txt
  - 102225-023115PM.csv (removed -latest)
  - 102225-023330PM-latest.md (new file)
```

## 🔧 Requirements

### Python Version
- Python 3.8 or higher

### Python Packages
- pydantic >= 2.0.0
- PyYAML >= 6.0
- watchdog >= 3.0.0

All automatically installed by `setup.py`

### External Tools
- **Claude Code CLI** (required for full functionality)
  - The service will run without it, but Claude Code execution will fail
  - Install from: https://docs.claude.com

## 🎯 Usage Patterns

### Run with default config
```bash
python main.py
```

### Run with custom config
```bash
python main.py /path/to/custom-config.yaml
```

### Stop the service
Press `Ctrl+C` in the terminal

### Check logs
```bash
cat test-assistant.log
```

## 🔍 What Happens Behind the Scenes

1. **Service Starts**
   - Loads configuration from config.yaml
   - Validates settings with Pydantic
   - Initializes watchdog observer
   - Starts monitoring directory

2. **File Detected**
   - Watchdog catches file creation event
   - Checks file extension (if filtering enabled)
   - Waits 0.5s to ensure file is fully written

3. **File Processing**
   - Finds any existing file with `-latest` suffix
   - Removes `-latest` from old file
   - Generates timestamp (local system time)
   - Renames new file with `timestamp-latest` format

4. **Claude Code Execution**
   - Constructs command: `claude-code "prompt /path/to/file"`
   - Executes command with 5-minute timeout
   - Captures stdout and stderr
   - Displays formatted output in terminal

5. **Ready for Next File**
   - Returns to watching state
   - Logs all actions to test-assistant.log
   - Waits for next file...

## 📊 Log Output

The service creates `test-assistant.log` with detailed information:

```
2025-10-22 14:30:15,123 - __main__ - INFO - Initializing test-assistant service...
2025-10-22 14:30:15,456 - __main__ - INFO - Configuration loaded from: config.yaml
2025-10-22 14:30:22,345 - event_handler - INFO - New file detected: report.txt
2025-10-22 14:30:22,456 - file_handler - INFO - Renaming new file: report.txt -> 102225-023022PM-latest.txt
2025-10-22 14:30:22,567 - claude_runner - INFO - Running claude-code with file: /home/user/test-assistant-watch/102225-023022PM-latest.txt
```

## 🐛 Troubleshooting

### Problem: claude-code not found
**Error Message:**
```
⚠️  WARNING: claude-code CLI is not available!
```

**Solution:**
1. Install Claude Code CLI from https://docs.claude.com
2. Ensure it's in your system PATH
3. Test: `claude-code --version`

### Problem: Configuration error
**Error Message:**
```
❌ Failed to load configuration: Watch path does not exist
```

**Solution:**
1. Check `watch_path` in config.yaml
2. Ensure directory exists
3. Use absolute path or correct relative path

### Problem: Files not detected
**Possible Causes:**
1. Wrong file extensions in config
2. Files moved (not created) into directory
3. Permission issues

**Solution:**
1. Set `file_extensions: []` to watch all files
2. Create files directly in watch directory
3. Check directory permissions
4. Review `test-assistant.log` for errors

### Problem: Permission denied
**Solution:**
- Ensure read/write permissions on watch directory
- Check if you can create files manually in the directory

## 💡 Best Practices

1. **Dedicated Terminal**: Run test-assistant in one terminal, work in another
2. **Start Simple**: Use default config first, customize later
3. **Test First**: Run `test_tool.py` to verify everything works
4. **Check Logs**: Review `test-assistant.log` for detailed operation info
5. **One at a Time**: Service processes files sequentially to avoid race conditions

## 🔐 Security Notes

- Service only monitors the configured directory
- No network access (except Claude Code CLI)
- All operations logged
- File permissions preserved during renaming

## 📚 Additional Resources

- **Full Documentation**: See `README.md`
- **Quick Reference**: See `QUICKSTART.md`
- **Example Session**: See `EXAMPLE_SESSION.md`
- **Claude Docs**: https://docs.claude.com

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files
3. Verify configuration
4. Test with `test_tool.py`

## 📄 License

MIT License - Free to use and modify

---

**Made with ❤️ using Python, Pydantic, and YAML**
