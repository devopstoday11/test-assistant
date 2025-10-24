# Test-Assistant Quick Reference

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure watch directory (edit config.yaml)
watch_path: "/path/to/your/folder"

# 3. Run
python main.py
```

---

## ⚙️ Configuration Cheat Sheet

| Option | Default | Options | Purpose |
|--------|---------|---------|---------|
| `watch_path` | **REQUIRED** | Any valid path | Directory to monitor |
| `claude_prompt` | **REQUIRED** | Any text | Prompt for Claude CLI |
| `file_extensions` | `[]` (all) | `[".txt", ".py"]` | Filter by extension |
| `dry_run` | `false` | `true`/`false` | Test without Claude |
| `timestamp_format` | `mmddyy-HH-MM-SS-AMPM` | See below | Timestamp style |
| `process_existing_files` | `false` | `true`/`false` | Process on startup |
| `log_level` | `INFO` | `DEBUG`/`INFO`/`WARNING`/`ERROR` | Verbosity |

### Timestamp Formats

| Format | Example Output |
|--------|----------------|
| `mmddyy-HH-MM-SS-AMPM` | `102325-10-07-50-AM` |
| `mmddyy-HHMMSS-AMPM` | `102325-100750-AM` |
| `mmddyy-HH:MM:SS-AMPM` | `102325-10:07:50-AM` |

---

## 🧪 Testing

```bash
# Run all 17 unit tests
python test_cheat_tool.py

# Test file renaming only (no Claude)
# Set dry_run: true in config.yaml, then:
python main.py

# Manual integration test
python test_tool.py
```

---

## 🎯 Common Use Cases

### Use Case 1: Test File Renaming

```yaml
dry_run: true
timestamp_format: "mmddyy-HH-MM-SS-AMPM"
```

### Use Case 2: Production with Specific Extensions

```yaml
dry_run: false
file_extensions: [".txt", ".md", ".py"]
log_level: "INFO"
```

### Use Case 3: Process Existing Files on Startup

```yaml
process_existing_files: true
file_stability_timeout: 10.0  # For large files
```

### Use Case 4: Debug Mode

```yaml
log_level: "DEBUG"
dry_run: true
```

---

## 📊 File Workflow

```
1. File created → test.txt
2. Added to queue → [test.txt]
3. Wait for stability → Check file size
4. Find existing -latest → 102325-09-00-00-AM-latest.txt
5. Remove -latest → 102325-09-00-00-AM.txt
6. Rename new file → 102325-10-07-50-AM-latest.txt
7. Trigger Claude CLI → claude -p "prompt /path/to/file"
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `claude: command not found` | Install Claude CLI or use `dry_run: true` |
| `Watch path does not exist` | Update `watch_path` in config.yaml |
| Files not detected | Check `file_extensions` setting |
| Tests fail | Normal for path resolution on macOS |
| Large files timeout | Increase `file_stability_timeout` |

---

## 📁 File Structure

```
test-assistant/
├── main.py              # Service entry point
├── config.yaml          # Configuration (EDIT THIS!)
├── config_model.py      # Pydantic config models
├── file_handler.py      # File renaming logic
├── claude_runner.py     # Claude CLI integration
├── event_handler.py     # Watchdog event handler
├── test_test_assistant.py   # Unit tests (17 tests)
├── test_tool.py         # Manual integration test
├── setup.py             # Initial setup script
├── requirements.txt     # Dependencies
├── CLAUDE.md            # Full documentation
└── test-assistant.log       # Log file (generated)
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop service gracefully |

---

## 🔍 Log Files

```bash
# View real-time logs
tail -f test-assistant.log

# View last 50 lines
tail -50 test-assistant.log

# Search for errors
grep ERROR test-assistant.log
```

---

## 🎨 Example Configurations

### Minimal (Required Only)

```yaml
watch_path: "/Users/you/Desktop/test"
claude_prompt: "Summarize:"
```

### Recommended

```yaml
watch_path: "/Users/you/Desktop/test"
claude_prompt: "Analyze and summarize this file:"
file_extensions: [".txt", ".md"]
dry_run: false
timestamp_format: "mmddyy-HH-MM-SS-AMPM"
log_level: "INFO"
```

### Development/Testing

```yaml
watch_path: "/tmp/test-folder"
claude_prompt: "Test prompt:"
dry_run: true
log_level: "DEBUG"
process_existing_files: true
```

---

## 🚨 Critical Commands

```bash
# Before first run
python setup.py

# Check Claude CLI
claude --version

# Run tests
python test_cheat_tool.py

# Start service
python main.py

# Stop service
Ctrl+C
```

---

## 📞 Quick Help

- Full documentation: See `CLAUDE.md`
- Improvements summary: See `IMPROVEMENTS_SUMMARY.md`
- Test results: Run `python test_cheat_tool.py`
- Original README: See `README.md`

---

**Version:** 2.0 (Enhanced)
**Tests:** 17/17 passing ✓
**Status:** Production Ready ✅
