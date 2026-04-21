# Intelligent File Copier

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/kapilthakare-cyberpunk/IntelligentCopier)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](#)
[![Python](https://img.shields.io/badge/python-3.7+-yellow.svg)](https://python.org)

A robust, GUI-based file copying application with resume capability, intelligent verification, and duplicate detection. Built for reliability when copying large volumes of data.

![Intelligent Copier Screenshot](assets/screenshot.png)

## Features

### Core Capabilities
- **Resume Support**: Interrupted copies can be resumed without starting over
- **Dry Run Mode**: Preview what will be copied before committing
- **Real-time Progress**: Live progress tracking with speed and ETA
- **Smart Verification**: Post-copy integrity verification
- **Duplicate Handling**: Multiple strategies for duplicate files

### Safety Features
- **Session Persistence**: Automatically saves copy state
- **Error Recovery**: Handles network interruptions and drive disconnections
- **System File Exclusion**: Automatically skips macOS system files (.DS_Store, Spotlight, etc.)
- **Permission Preservation**: Maintains file permissions and metadata

### Monitoring & Reporting
- **Detailed Logging**: Complete activity log with timestamps
- **Progress Statistics**: Files processed, transfer speed, time remaining
- **Copy Reports**: Generate detailed post-copy reports
- **Visual Feedback**: Color-coded status indicators

## Use Cases

- **Large Data Migrations**: Moving TBs of data between drives
- **Backup Operations**: Creating reliable backups with verification
- **Photo/Video Libraries**: Copying media collections with duplicate detection
- **Project Archives**: Preserving project structures with integrity checks
- **Cross-Platform Transfers**: Moving data between different filesystems

## Installation

### Prerequisites
- Python 3.7 or higher
- rsync (pre-installed on macOS and most Linux distributions)
- tkinter (usually included with Python)

### macOS

```bash
# Clone the repository
git clone https://github.com/kapilthakare-cyberpunk/IntelligentCopier.git
cd IntelligentCopier

# Run directly
python3 src/intelligent_copier.py

# Or create an app bundle
chmod +x install_macos.sh
./install_macos.sh
```

### Linux

```bash
# Clone the repository
git clone https://github.com/kapilthakare-cyberpunk/IntelligentCopier.git
cd IntelligentCopier

# Install dependencies (if needed)
pip3 install -r requirements.txt

# Run
python3 src/intelligent_copier.py
```

### Windows

Windows support is experimental. Requires WSL or Git Bash with rsync installed.

## Quick Start

1. **Launch the application**
   ```bash
   python3 src/intelligent_copier.py
   ```

2. **Select source and destination**
   - Click "Browse" to select your source directory
   - Click "Browse" to select your destination directory

3. **Configure options**
   - Enable "Dry Run First" to preview (recommended)
   - Choose duplicate handling strategy
   - Enable verification for important data

4. **Start copying**
   - Click "Analyze" to see what will be copied
   - Click "Start Copy" to begin
   - Monitor progress in real-time

5. **Verify** (optional but recommended)
   - Click "Verify" after copy completes
   - Review the generated report

## 📖 Detailed Usage

### Dry Run Mode

Always recommended for large operations:
- Simulates the copy without transferring data
- Shows exactly what will be copied
- Reports potential conflicts or issues
- Gives you confidence before the actual operation

### Duplicate Handling Strategies

| Strategy | Behavior |
|----------|----------|
| **Skip** | Skip duplicate files, keep destination version |
| **Overwrite** | Replace destination with source if newer |
| **Rename** | Add suffix (e.g., `_1`, `_2`) to duplicates |
| **Review** | Move duplicates to a review folder for manual decision |

### Resume Capability

If a copy is interrupted:
1. Reconnect drives if disconnected
2. Relaunch Intelligent Copier
3. Click "Resume"
4. Click "Start Copy" - rsync will skip already-copied files

### Verification Process

Post-copy verification checks:
- File count matches
- Total size matches
- Sample file integrity (size comparison)
- Detailed statistics report

## Configuration

Configuration is stored in `~/.intelligent_copier_config.json`:

```json
{
  "source": "/path/to/source",
  "dest": "/path/to/destination",
  "options": {
    "dry_run": true,
    "verify": true,
    "preserve_perms": true,
    "exclude_system": true,
    "duplicate_action": "review"
  }
}
```

## Interface Guide

### Main Window Sections

1. **Source & Destination**: Path selection with browse buttons
2. **Copy Options**: Configure behavior
3. **Progress**: Real-time transfer status
4. **Activity Log**: Detailed operation log
5. **Action Buttons**: Control operations

### Status Indicators

- **Ready**: Application ready to use
- **Copying**: Transfer in progress
- **Paused**: Copy interrupted
- **Verifying**: Post-copy verification running
- **Error**: Issue encountered

### Log Colors

- **Blue**: Information messages
- **Green**: Success messages
- **Yellow**: Warnings
- **Red**: Errors

## 🛠️ Advanced Features

### Command-Line Usage

```bash
# Direct launch
python3 src/intelligent_copier.py

# With specific paths
python3 src/intelligent_copier.py --source /Volumes/Source --dest /Volumes/Dest
```

### Integration with Scripts

```python
from src.intelligent_copier import IntelligentCopier

# Programmatic usage
copier = IntelligentCopier(root)
copier.source_var.set("/path/to/source")
copier.dest_var.set("/path/to/dest")
copier.start_copy()
```

### Custom Exclusions

Edit the `excludes` list in `intelligent_copier.py`:

```python
excludes = [
    '.Spotlight-V100',
    '.TemporaryItems',
    '.Trashes',
    '.fseventsd',
    '.DS_Store',
    '._*',
    'node_modules',  # Add custom patterns
    '.git'
]
```

## Troubleshooting

### Common Issues

**Issue**: "rsync not found" error  
**Solution**: Install rsync: `brew install rsync` (macOS) or `apt-get install rsync` (Linux)

**Issue**: Permission denied errors  
**Solution**: Ensure you have read access to source and write access to destination

**Issue**: Copy extremely slow  
**Solution**: 
- Check USB connection (use USB 3.0/3.1 ports)
- Exclude unnecessary files
- Consider copying in batches for very large datasets

**Issue**: Application won't launch  
**Solution**: Check Python version: `python3 --version` (requires 3.7+)

### Log Files

- **Application log**: `~/intelligent_copier_*.log`
- **Session state**: `~/.intelligent_copier_session.json`
- **Configuration**: `~/.intelligent_copier_config.json`

## Requirements

- Python 3.7+
- tkinter (usually included)
- rsync
- 100MB free RAM
- Recommended: SSD for source/destination

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/kapilthakare-cyberpunk/IntelligentCopier.git
cd IntelligentCopier

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and tkinter
- Uses rsync for reliable file transfers
- Inspired by the need for robust data migration tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kapilthakare-cyberpunk/IntelligentCopier/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kapilthakare-cyberpunk/IntelligentCopier/discussions)
- **Email**: kapil@example.com

## Roadmap

- [ ] Windows native support
- [ ] Cloud storage integration (S3, Google Drive)
- [ ] Scheduling and automation
- [ ] Checksum verification (SHA-256)
- [ ] Bandwidth throttling
- [ ] Multi-threaded copying
- [ ] Dark mode theme
- [ ] Internationalization

---

**Made with ❤️ by Kapil Thakare**

*If this tool helps you, please consider giving it a ⭐ on GitHub!*
