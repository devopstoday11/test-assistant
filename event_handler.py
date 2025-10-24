"""Watchdog event handler for test-assistant."""
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from typing import List
import logging
import queue
import threading

from file_handler import FileHandler
from claude_runner import ClaudeCodeRunner

logger = logging.getLogger(__name__)


class TestAssistantEventHandler(FileSystemEventHandler):
    """Event handler for file system changes."""

    def __init__(
        self,
        watch_dir: str,
        claude_runner: ClaudeCodeRunner,
        file_handler: FileHandler,
        file_extensions: List[str]
    ):
        """Initialize event handler.

        Args:
            watch_dir: Directory being watched
            claude_runner: Claude CLI runner instance
            file_handler: File handler instance with configured settings
            file_extensions: List of file extensions to watch (empty = all)
        """
        super().__init__()
        self.watch_dir = Path(watch_dir)
        self.file_handler = file_handler
        self.claude_runner = claude_runner
        self.file_extensions = file_extensions

        # Queue-based processing instead of boolean flag
        self.file_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        self._shutdown = False
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on extension.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be processed
        """
        # If no extensions specified, process all files
        if not self.file_extensions:
            return True

        # Check if file extension matches any in the list
        return file_path.suffix.lower() in [ext.lower() for ext in self.file_extensions]

    def _process_queue(self):
        """Worker thread that processes files from the queue."""
        while not self._shutdown:
            try:
                # Wait for a file with timeout to allow checking shutdown flag
                file_path = self.file_queue.get(timeout=1.0)

                if file_path is None:  # Shutdown signal
                    break

                self._process_file(file_path)
                self.file_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in queue processing: {e}", exc_info=True)

    def _process_file(self, file_path: Path):
        """Process a single file.

        Args:
            file_path: Path to the file to process
        """
        try:
            logger.info(f"Processing file from queue: {file_path.name}")
            print(f"\n📁 PROCESSING FILE: {file_path.name}")

            # Wait for file to be stable (completely written)
            if not self.file_handler.wait_for_file_stability(file_path):
                logger.warning(f"File not stable, skipping: {file_path.name}")
                return

            # Check if file still exists
            if not file_path.exists():
                logger.warning(f"File disappeared: {file_path.name}")
                return

            # Process the file (rename with timestamp-latest)
            renamed_path = self.file_handler.process_new_file(file_path)

            print(f"✅ FILE RENAMED: {renamed_path.name}\n")

            # Trigger claude CLI
            self.claude_runner.run_claude_code(renamed_path)

            print(f"\n👀 Watching for next file...\n")

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            print(f"\n❌ ERROR: {e}\n")

    def on_created(self, event):
        """Handle file creation events.

        Args:
            event: File system event
        """
        # Ignore directory creation
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if we should process this file
        if not self.should_process_file(file_path):
            logger.info(f"Skipping file (extension not watched): {file_path.name}")
            return

        logger.info(f"New file detected: {file_path.name}")
        print(f"\n📁 NEW FILE DETECTED: {file_path.name}")

        # Add to queue for processing
        self.file_queue.put(file_path)
        logger.debug(f"File added to queue: {file_path.name}")

    def shutdown(self):
        """Shutdown the event handler gracefully."""
        logger.info("Shutting down event handler...")
        self._shutdown = True
        self.file_queue.put(None)  # Signal worker to stop
        self.worker_thread.join(timeout=5)
