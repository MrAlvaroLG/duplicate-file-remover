Here's the English version of your README.md:

```markdown
# Duplicate File Cleaner

A tool to remove duplicate files using MD5 hash comparison. Cross-platform compatible.

## Features

- Precise detection using MD5 hashes
- Command-line interface (CLI)
- Recursive search in subdirectories
- Interactive confirmation mode
- Automatic deletion option
- Real-time progress feedback

## Requirements

- Python 3.6 or higher
- Write permissions in target directories

## Installation

```bash
git clone https://github.com/yourusername/duplicate-file-cleaner.git
cd duplicate-file-cleaner
```

## Basic Usage

**Windows:**
```cmd
python remove_duplicates.py "C:\path\to\directory"
```

**Linux/macOS:**
```bash
python3 remove_duplicates.py "/path/to/directory"
```

**Automatic deletion (no confirmation):**
```bash
python3 remove_duplicates.py "/path/to/directory" -y
```

## Command-Line Options

| Option        | Description                                  |
|---------------|----------------------------------------------|
| `directory`   | Path to analyze (required)                  |
| `-y`          | Delete duplicates without confirmation      |

## Precautions

1. **Backup** important files first
2. Files are **permanently deleted** (not sent to Trash/Recycle Bin)
3. First file in each duplicate group is preserved
4. Test first with non-critical directories

## Compatibility

| System        | Tested Versions           |
|---------------|------------------------------|
| Windows       | 10, 11                       |
| Linux         | Ubuntu 20.04+, Fedora 35+    |
| macOS         | Monterey 12.0+               |

**Disclaimer:** Use this software at your own risk. The author is not responsible for data loss.
```
