"""
DEBUG VERSION - File Integrity Checker
"""

import os
import json
import hashlib
import time
from datetime import datetime
from colorama import Fore, init
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

init(autoreset=True)

HASH_FILE = "hashes.json"
LOG_FILE = "activity.log"
IGNORE_FILES = {"hashes.json", "activity.log"}

print(Fore.CYAN + "=== DEBUG MODE ENABLED ===")

def log_activity(message, event_type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.WHITE}[{timestamp}] {event_type}: {message}")
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {event_type}\n{message}\n")


class DebugHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        """Catch ALL events for debugging"""
        print(f"{Fore.MAGENTA}EVENT DETECTED → {event.event_type}: {event.src_path}")
        
        if event.is_directory:
            return
            
        if os.path.basename(event.src_path) in IGNORE_FILES:
            print(f"{Fore.YELLOW}Ignored: {event.src_path}")
            return

        if event.event_type in ['created', 'modified']:
            print(f"{Fore.YELLOW}Processing {event.event_type} event...")
            # For now just log
            log_activity(event.src_path, event.event_type.upper())
            
        elif event.event_type == 'deleted':
            log_activity(event.src_path, "DELETED")


def main():
    print(Fore.CYAN + """
=====================================
     FILE INTEGRITY CHECKER - DEBUG
=====================================
""")

    directory = input("\nEnter directory path: ").strip()
    directory = os.path.abspath(directory)

    if not os.path.exists(directory):
        print(f"{Fore.RED}Directory not found!")
        return

    print(f"\n📁 Monitoring (Debug): {directory}")
    print(f"{Fore.CYAN}Starting PollingObserver... (This may take a few seconds)\n")

    event_handler = DebugHandler()
    observer = PollingObserver(timeout=1.0)
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    print(f"{Fore.GREEN}✅ Monitoring ACTIVE - Make changes in {directory} now...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{Fore.YELLOW}Stopped.")
    finally:
        observer.join()


if __name__ == "__main__":
    main()
