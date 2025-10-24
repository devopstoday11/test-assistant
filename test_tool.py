#!/usr/bin/env python3
"""Test script to demonstrate test-assistant functionality."""
import time
from pathlib import Path
from config_model import TestAssistantConfig


def create_test_file(watch_dir: Path, filename: str, content: str):
    """Create a test file in the watch directory."""
    file_path = watch_dir / filename
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Created test file: {filename}")
    return file_path


def main():
    """Run tests."""
    print("=" * 80)
    print("TEST-ASSISTANT TEST SCRIPT")
    print("=" * 80)
    print()
    
    # Load config
    try:
        config = TestAssistantConfig.from_yaml("config.yaml")
        print(f"✅ Configuration loaded")
        print(f"📂 Watch directory: {config.watch_path}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    watch_dir = Path(config.watch_path)
    
    # Check if watch directory exists
    if not watch_dir.exists():
        print(f"❌ Watch directory does not exist: {watch_dir}")
        print(f"   Run setup.py first")
        return
    
    print(f"\n📝 This script will create test files in the watch directory.")
    print(f"   Make sure test-assistant is running in another terminal!")
    print()
    
    input("Press Enter to create test files (or Ctrl+C to cancel)...")
    print()
    
    # Create test files with delays
    test_files = [
        ("test1.txt", "This is the first test file.\nCheat-tool should rename this."),
        ("test2.py", "# Python test file\nprint('Hello from test2')"),
        ("test3.md", "# Markdown Test\n\nThis is a markdown file for testing.")
    ]
    
    for i, (filename, content) in enumerate(test_files, 1):
        print(f"\n[Test {i}/{len(test_files)}]")
        create_test_file(watch_dir, filename, content)
        print(f"⏳ Waiting 5 seconds before next file...")
        time.sleep(5)

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print(f"\nCheck your test-assistant terminal for processing output.")
    print(f"Check {watch_dir} to see renamed files.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
