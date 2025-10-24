"""Main service for test-assistant."""
import logging
import sys
from pathlib import Path
from watchdog.observers import Observer
import time

from config_model import TestAssistantConfig
from claude_runner import ClaudeCodeRunner
from file_handler import FileHandler
from event_handler import TestAssistantEventHandler

logger = logging.getLogger(__name__)


class TestAssistantService:
    """Main service for test-assistant."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the service.

        Args:
            config_path: Path to configuration YAML file
        """
        # Load configuration first
        try:
            self.config = TestAssistantConfig.from_yaml(config_path)
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            raise

        # Configure logging with level from config
        self._setup_logging()

        logger.info("Initializing test-assistant service...")
        logger.info(f"Configuration loaded from: {config_path}")
        logger.info(f"Watch path: {self.config.watch_path}")
        logger.info(f"Claude prompt: {self.config.claude_prompt}")
        logger.info(f"File extensions: {self.config.file_extensions or 'ALL'}")
        logger.info(f"Dry run mode: {self.config.dry_run}")
        logger.info(f"Timestamp format: {self.config.timestamp_format}")
        logger.info(f"Process existing files: {self.config.process_existing_files}")

        # Validate watch path exists
        watch_path = Path(self.config.watch_path)
        if not watch_path.exists() or not watch_path.is_dir():
            raise ValueError(f"Watch path does not exist or is not a directory: {self.config.watch_path}")

        # Initialize Claude runner
        self.claude_runner = ClaudeCodeRunner(
            self.config.claude_prompt,
            dry_run=self.config.dry_run
        )

        # Check if claude CLI is available (skip in dry-run mode)
        if not self.config.dry_run:
            if not self.claude_runner.check_claude_code_available():
                logger.warning("⚠️  claude CLI not found or not available")
                print("\n⚠️  WARNING: claude CLI is not available!")
                print("The service will run, but claude execution will fail.")
                print("Please ensure claude CLI is installed and in your PATH.\n")
            else:
                logger.info("✅ claude CLI is available")
        else:
            logger.info("🔸 Dry run mode enabled - skipping claude CLI check")

        # Initialize file handler
        self.file_handler = FileHandler(
            watch_dir=self.config.watch_path,
            timestamp_format=self.config.timestamp_format,
            stability_timeout=self.config.file_stability_timeout,
            stability_check_interval=self.config.file_stability_check_interval
        )

        # Initialize event handler
        self.event_handler = TestAssistantEventHandler(
            watch_dir=self.config.watch_path,
            claude_runner=self.claude_runner,
            file_handler=self.file_handler,
            file_extensions=self.config.file_extensions
        )

        # Initialize observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            self.config.watch_path,
            recursive=False
        )

    def _setup_logging(self):
        """Setup logging with configured level."""
        log_level = getattr(logging, self.config.log_level, logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test-assistant.log'),
                logging.StreamHandler(sys.stdout)
            ],
            force=True  # Override any existing configuration
        )
    
    def _process_existing_files(self):
        """Process existing files in watch directory on startup."""
        watch_path = Path(self.config.watch_path)
        existing_files = []

        # Find all files matching configured extensions
        for file_path in watch_path.iterdir():
            if not file_path.is_file():
                continue

            if self.config.file_extensions:
                if file_path.suffix.lower() not in [ext.lower() for ext in self.config.file_extensions]:
                    continue

            # Skip files that already have the timestamp format or -latest suffix
            if "-latest" in file_path.stem or self._looks_like_timestamp(file_path.stem):
                logger.debug(f"Skipping already processed file: {file_path.name}")
                continue

            existing_files.append(file_path)

        if not existing_files:
            logger.info("No existing files to process")
            return

        print(f"\n📦 Found {len(existing_files)} existing file(s) to process")
        logger.info(f"Processing {len(existing_files)} existing files...")

        for file_path in sorted(existing_files, key=lambda p: p.stat().st_mtime):
            logger.info(f"Processing existing file: {file_path.name}")
            self.event_handler.file_queue.put(file_path)

        print(f"✅ Queued {len(existing_files)} file(s) for processing\n")

    def _looks_like_timestamp(self, filename: str) -> bool:
        """Check if filename looks like it already has a timestamp."""
        # Simple heuristic: check if it starts with digits in mmddyy format
        import re
        return bool(re.match(r'^\d{6}-', filename))

    def start(self):
        """Start the service."""
        logger.info("Starting test-assistant service...")

        print("\n" + "="*80)
        print("🚀 TEST-ASSISTANT SERVICE STARTED")
        print("="*80)
        print(f"📂 Watching directory: {self.config.watch_path}")
        print(f"🤖 Claude prompt: {self.config.claude_prompt}")
        if self.config.file_extensions:
            print(f"📄 Watching extensions: {', '.join(self.config.file_extensions)}")
        else:
            print(f"📄 Watching: ALL file types")
        print(f"⚙️  Timestamp format: {self.config.timestamp_format}")
        print(f"🔸 Dry run mode: {'ENABLED' if self.config.dry_run else 'DISABLED'}")
        print(f"📊 Log level: {self.config.log_level}")
        print("="*80)

        # Process existing files if configured
        if self.config.process_existing_files:
            self._process_existing_files()

        print("\n👀 Waiting for new files...")
        print("Press Ctrl+C to stop the service\n")

        self.observer.start()

        try:
            while True:
                # Check if watch directory still exists
                if not Path(self.config.watch_path).exists():
                    logger.error("Watch directory no longer exists!")
                    print("\n❌ ERROR: Watch directory was deleted or is no longer accessible")
                    print("Stopping service...\n")
                    break

                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the service."""
        logger.info("Stopping test-assistant service...")
        print("\n\n🛑 Stopping test-assistant service...")

        # Shutdown event handler first
        self.event_handler.shutdown()

        # Stop observer
        self.observer.stop()
        self.observer.join()

        logger.info("Service stopped")
        print("✅ Service stopped successfully\n")


def main():
    """Main entry point."""
    # Check for config file argument
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    # Check if config file exists
    if not Path(config_path).exists():
        print(f"❌ Error: Configuration file not found: {config_path}")
        print(f"\nUsage: python main.py [config_path]")
        print(f"Default: python main.py config.yaml\n")
        sys.exit(1)
    
    # Start the service
    try:
        service = TestAssistantService(config_path)
        service.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ FATAL ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
