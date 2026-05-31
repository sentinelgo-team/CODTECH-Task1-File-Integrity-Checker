# File Integrity Checker

**CODTECH Cyber Security Internship Task 1**

A robust cybersecurity tool that monitors file integrity using **SHA-256 hashing** and **real-time detection** with the Watchdog library.

## Features

- SHA-256 cryptographic hashing
- Real-time file monitoring (Create, Modify, Delete)
- Persistent JSON hash database
- Activity logging with timestamps
- Colored terminal alerts
- Self-exclusion of monitoring files
- Professional error handling

## Technologies Used

- Python 3
- hashlib (SHA-256)
- watchdog
- colorama
- json

## Installation

```bash
git clone https://github.com/sentinelgo-team/CODTECH-Task1-File-Integrity-Checker.git
cd CODTECH-Task1-File-Integrity-Checker
pip install -r requirements.txt
```

## Usage

```bash
python integrity_checker.py
```

Enter the directory path when prompted.

## Author

Ravi  
Cyber Security Intern - CODTECH