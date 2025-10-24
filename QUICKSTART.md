# Cheat-Tool Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup
```bash
python setup.py
```
This will:
- Install dependencies
- Create a watch directory (`~/test-assistant-watch`)
- Update config.yaml with the watch directory

### Step 2: Configure (Optional)
Edit `config.yaml` to customize:
```yaml
watch_path: "/path/to/your/directory"  # Change watch location
claude_prompt: "Your custom prompt:"    # Customize Claude prompt
file_extensions: [".txt", ".py"]        # Filter specific file types
```

### Step 3: Run
```bash
python main.py
```

The service will now:
- ✅ Watch for new files
- ✅ Rename them with timestamp-latest
- ✅ Trigger Claude Code CLI
- ✅ Display output in terminal

## 📋 Common Commands

### Start the service
```bash
python main.py
```

### Start with custom config
```bash
python main.py /path/to/config.yaml
```

### Stop the service
Press `Ctrl+C` in the terminal

### Test the tool
In a separate terminal:
```bash
python test_tool.py
```

### Create test file manually
```bash
echo "Test content" > ~/test-assistant-watch/test.txt
```

## 🎯 Usage Examples

### Example 1: Watch only Python files
```yaml
file_extensions:
  - ".py"
```

### Example 2: Watch all files
```yaml
file_extensions: []
```

### Example 3: Custom Claude prompt
```yaml
claude_prompt: "Review this code for security issues:"
```

### Example 4: Custom watch directory
```yaml
watch_path: "/home/user/projects/incoming"
```

## 📊 What Happens When You Add a File

1. **File appears**: `myfile.txt` is created in watch directory
2. **Processing starts**:
   - Old file with `-latest` (if exists) → loses the suffix
   - New file → renamed to `102225-023022PM-latest.txt`
3. **Claude Code runs**:
   - Command: `claude-code "Your prompt /path/to/102225-023022PM-latest.txt"`
   - Output displayed in terminal
4. **Ready for next file**: Service continues watching

## ⚙️ Configuration Reference

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `watch_path` | string | Directory to monitor | Required |
| `claude_prompt` | string | Prompt for Claude Code | Required |
| `file_extensions` | list | File types to watch | `[]` (all) |

## 🐛 Troubleshooting

### Problem: "claude-code not found"
**Solution**: Install Claude Code CLI and ensure it's in your PATH

### Problem: "Watch path does not exist"
**Solution**: Create the directory or update `watch_path` in config.yaml

### Problem: Files not detected
**Solution**: 
- Check `file_extensions` matches your files
- Ensure files are created (not moved) into directory
- Check `test-assistant.log` for errors

### Problem: Permission denied
**Solution**: Ensure you have read/write permissions for watch directory

## 📁 File Structure

```
test-assistant/
├── main.py           # Start here
├── config.yaml       # Edit your settings here
├── setup.py          # Run once for initial setup
├── test_tool.py      # Test the tool
├── requirements.txt  # Dependencies
└── README.md         # Full documentation
```

## 💡 Tips

1. **Run in dedicated terminal**: Keep test-assistant running in one terminal, use another for work
2. **Check logs**: `test-assistant.log` contains detailed operation logs
3. **Test first**: Use `test_tool.py` to verify everything works
4. **Start simple**: Begin with default config, customize later
5. **One at a time**: Service processes one file at a time to avoid conflicts

## 🔗 Resources

- Full README: [README.md](README.md)
- Configuration Models: `config_model.py`
- Claude Docs: https://docs.claude.com
