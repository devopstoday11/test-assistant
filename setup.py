#!/usr/bin/env python3
"""Quick setup script for test-assistant."""
import os
import sys
from pathlib import Path


def main():
    """Setup script for test-assistant."""
    print("=" * 80)
    print("TEST-ASSISTANT SETUP")
    print("=" * 80)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Your version: {sys.version}")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    os.system("pip install -r requirements.txt --quiet")
    print("✅ Dependencies installed")
    
    # Create a default watch directory
    watch_dir = Path.home() / "test-assistant-watch"
    if not watch_dir.exists():
        watch_dir.mkdir(parents=True)
        print(f"\n✅ Created watch directory: {watch_dir}")
    else:
        print(f"\n✅ Watch directory exists: {watch_dir}")
    
    # Update config.yaml with the watch directory
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Replace the watch_path
        config_content = config_content.replace(
            'watch_path: "/path/to/watch"',
            f'watch_path: "{watch_dir}"'
        )
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Updated config.yaml with watch directory")
    
    # Check if claude-code is available
    print("\n🔍 Checking for claude-code CLI...")
    result = os.system("claude-code --version > /dev/null 2>&1")
    if result == 0:
        print("✅ claude-code CLI is available")
    else:
        print("⚠️  claude-code CLI not found")
        print("   Please install claude-code CLI to use this tool")
        print("   Visit: https://docs.claude.com for installation instructions")
    
    print("\n" + "=" * 80)
    print("SETUP COMPLETE!")
    print("=" * 80)
    print(f"\n📂 Watch directory: {watch_dir}")
    print(f"⚙️  Configuration: {config_path.absolute()}")
    print("\n🚀 To start test-assistant, run:")
    print("   python main.py")
    print("\n📝 To test, create a file in the watch directory:")
    print(f"   echo 'Hello World' > {watch_dir}/test.txt")
    print()


if __name__ == "__main__":
    main()
