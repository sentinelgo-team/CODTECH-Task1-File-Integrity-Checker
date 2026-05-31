"""
File Integrity Checker - CODTECH Task 1 (Final Clean Version)
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

# Ignore temporary and system files
IGNORE_FILES = {
    "hashes.json", "activity.log", ".DS_Store", 
    "__pycache__", ".git"
}

def is_temp_file(filename):
    """Ignore temporary Office and system files"""
    temp_patterns = ['~', '.tmp', '.TMP', '.crdownload', '.lock']
    return any(filename.startswith(p) or filename.endswith(p) for p in temp_patterns)


def log_activity(message: str, event_type: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} {event_type}\n{message}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    if event_type == "MODIFIED":
        print(f"{Fore.RED}[MODIFIED] {message}")
    elif event_type == "NEW":
        print(f"{Fore.YELLOW}[NEW FILE] {message}")
    elif event_type == "DELETED":
        print(f"{Fore.RED}[DELETED] {message}")


def calculate_hash(file_path: str):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except PermissionError:
        return None
    except Exception:
        return None


class IntegrityEventHandler(FileSystemEventHandler):
    def __init__(self, directory):
        self.directory = os.path.abspath(directory)
        self.hashes = load_hashes()

    def on_modified(self, event):
        if event.is_directory or is_temp_file(os.path.basename(event.src_path)):
            return
        self._process_event(event.src_path, "MODIFIED")

    def on_created(self, event):
        if event.is_directory or is_temp_file(os.path.basename(event.src_path)):
            return
        self._process_event(event.src_path, "NEW")

    def on_deleted(self, event):
        if event.is_directory or is_temp_file(os.path.basename(event.src_path)):
            return
        rel_path = os.path.relpath(event.src_path, self.directory)
        if rel_path in self.hashes:
            del self.hashes[rel_path]
            save_hashes(self.hashes)
        log_activity(rel_path, "DELETED")

    def _process_event(self, file_path, event_type):
        file_hash = calculate_hash(file_path)
        if not file_hash:
            return

        rel_path = os.path.relpath(file_path, self.directory)

        if event_type == "NEW" or rel_path not in self.hashes:
            log_activity(rel_path, "NEW")
        elif self.hashes.get(rel_path, {}).get("hash") != file_hash:
            log_activity(rel_path, "MODIFIED")

        self.hashes[rel_path] = {
            "hash": file_hash,
            "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_hashes(self.hashes)


def load_hashes():
    if not os.path.exists(HASH_FILE):
        return {}
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_hashes(data):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def main():
    print(Fore.CYAN + """
=====================================
     FILE INTEGRITY CHECKER
        CODTECH TASK 1
   SHA-256 + Real-Time Monitoring
=====================================
""")

    directory = input("\nEnter directory path to monitor: ").strip()
    directory = os.path.abspath(directory)

    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"{Fore.RED}❌ Error: Invalid directory path!")
        return

    print(f"\n📁 Monitoring: {directory}\n")

    if not os.path.exists(HASH_FILE):
        print(f"{Fore.CYAN}Performing initial baseline scan...")
        # (Initial scan code remains same)
        file_hashes = {}
        for root, _, files in os.walk(directory):
            for file in files:
                if file in IGNORE_FILES or is_temp_file(file):
                    continue
                full_path = os.path.join(root, file)
                file_hash = calculate_hash(full_path)
                if file_hash:
                    rel_path = os.path.relpath(full_path, directory)
                    file_hashes[rel_path] = {
                        "hash": file_hash,
                        "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
        save_hashes(file_hashes)
        log_activity("Baseline Created Successfully", "BASELINE")
        print(f"{Fore.GREEN}✓ Initial baseline created!")
    else:
        print(f"{Fore.GREEN}✓ Baseline loaded.")

    print(f"{Fore.CYAN}🚀 Starting real-time monitoring... (Press Ctrl+C to stop)\n")

    event_handler = IntegrityEventHandler(directory)
    observer = PollingObserver()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{Fore.YELLOW}⏹️ Monitoring stopped.")
    finally:
        observer.join()


if __name__ == "__main__":
    main()
