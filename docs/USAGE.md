# Usage Guide

## Basic Workflow

### 1. Starting the Application

```bash
# From source
python3 src/intelligent_copier.py

# Or use the installed app
open "Intelligent Copier.app"
```

### 2. Setting Up a Copy Operation

#### Step 1: Select Source
- Click the "📂 Browse" button next to "Source"
- Navigate to and select the directory you want to copy from
- The path will appear in the text field

#### Step 2: Select Destination
- Click the "📂 Browse" button next to "Destination"
- Navigate to and select (or create) the directory you want to copy to
- The path will appear in the text field

#### Step 3: Configure Options

**Recommended Settings:**
- ✅ **Dry Run First**: Always enable for large operations
- ✅ **Verify After Copy**: Enable for critical data
- ✅ **Preserve Permissions**: Keep checked for backups
- ✅ **Exclude System Files**: Keep checked (skips .DS_Store, etc.)
- 🔄 **Duplicates**: Choose based on your needs:
  - `review` - Safest option, moves duplicates to review folder
  - `skip` - Fastest, keeps destination version
  - `overwrite` - Replaces with newer files
  - `rename` - Adds suffix to avoid conflicts

### 3. Analyzing (Optional but Recommended)

Click **"🔍 Analyze"** to:
- Count total files and directories
- Calculate total size
- Estimate copy time
- Check available space

This gives you a preview before committing to the operation.

### 4. Starting the Copy

Click **"▶️  Start Copy"** to begin.

**If Dry Run is enabled:**
1. A dry run will execute first
2. Review the preview in the log
3. Click "Yes" to proceed with actual copy

**During Copy:**
- Watch the progress bar
- Monitor transfer speed
- Check ETA (estimated time remaining)
- View current file being copied

### 5. Pausing (Optional)

Click **"⏸️  Pause"** to temporarily stop:
- Copy can be resumed later
- Already copied files are preserved
- Session is automatically saved

To resume, click **"⏸️  Resume"** (button changes to "▶️  Resume")

### 6. Verification (Recommended)

After copy completes:

Click **"✅ Verify"** to:
- Compare file counts (source vs destination)
- Compare total sizes
- Sample-check file integrity
- Generate verification report

### 7. Generating Reports

Click **"📊 Report"** to save a detailed copy report including:
- Timestamp and session ID
- Source and destination paths
- Total files and size
- List of top-level directories

## Advanced Features

### Session Management

**Auto-Save:**
- Sessions are automatically saved to `~/.intelligent_copier_session.json`
- Includes source, destination, and progress state

**Manual Resume:**
- Click **"🔄 Resume"** to load previous session
- Or restart app and it will prompt to resume

**Starting Fresh:**
- Select new source/destination to create new session
- Previous session is overwritten

### Excluding Files

By default, these are excluded:
- `.Spotlight-V100` - macOS Spotlight index
- `.TemporaryItems` - Temporary files
- `.Trashes` - Trash folder
- `.fseventsd` - File system events
- `.DS_Store` - macOS folder metadata
- `._*` - macOS resource forks
- `.sync.ffs_db` - FreeFileSync database

**Custom Exclusions:**
Edit the code to add custom patterns:

```python
excludes = [
    '.Spotlight-V100',
    '.TemporaryItems',
    # Add your patterns:
    'node_modules',
    '.git',
    '*.tmp'
]
```

### Duplicate Handling Details

| Strategy | What Happens | Use Case |
|----------|--------------|----------|
| **Skip** | Keeps destination version | Quick sync, trust destination |
| **Overwrite** | Replaces if source is newer | Update existing backup |
| **Rename** | Creates file_1, file_2, etc. | Preserve all versions |
| **Review** | Moves to _DUPLICATES_REVIEW/ | Manual inspection needed |

**Finding Duplicates:**
The app detects duplicates by:
1. MD5 hash comparison
2. Filename and size matching

### Performance Tips

1. **Use USB 3.0+ ports** - Significantly faster than USB 2.0
2. **Close other apps** - Reduces disk contention
3. **Disable real-time antivirus** - Temporarily for large copies
4. **Split very large operations** - Copy in chunks for better reliability
5. **Use "Skip" for duplicates** - Fastest duplicate strategy

## Troubleshooting

### Common Scenarios

**"Not enough space" error**
- Check destination available space
- Enable "Dry Run" first to estimate size
- Clean up destination or choose different location

**"Permission denied" error**
- Ensure read access to source
- Ensure write access to destination
- Try running with elevated permissions if needed

**"rsync not found" error**
```bash
# macOS
brew install rsync

# Linux
sudo apt-get install rsync  # Debian/Ubuntu
sudo yum install rsync       # RHEL/CentOS
```

**Copy seems frozen**
- Large files take time - check ETA
- Many small files slow down progress
- Check Activity Monitor for rsync process
- Look at transfer speed indicator

**Application crashes**
- Check log file: `~/intelligent_copier_*.log`
- Try with smaller directories first
- Ensure Python 3.7+
- Check system RAM (needs ~100MB free)

### Getting Help

1. Check the log file for error details
2. Review [README.md](../README.md) for setup instructions
3. Search [GitHub Issues](https://github.com/kapilthakare-cyberpunk/IntelligentCopier/issues)
4. Create new issue with:
   - Error message
   - Log file contents
   - Your operating system
   - Python version

## Best Practices

### Before Large Copies

1. ✅ **Always run Dry Run first**
2. ✅ **Analyze to see file count and size**
3. ✅ **Ensure destination has enough space**
4. ✅ **Check drive health** (Disk Utility on macOS)
5. ✅ **Close unnecessary applications**
6. ✅ **Connect to power** (for laptops)

### During Copy

1. 📊 **Monitor progress** periodically
2. 🔋 **Keep laptop plugged in**
3. 🚫 **Don't disconnect drives**
4. 💤 **Disable sleep mode** (System Preferences)

### After Copy

1. ✅ **Always verify important data**
2. 📄 **Save copy report**
3. 🔍 **Spot-check key files**
4. 💾 **Keep source until verified**

### For Critical Data

1. **3-2-1 Rule**:
   - 3 copies of important data
   - 2 different media types
   - 1 offsite

2. **Verify twice**:
   - Once immediately after copy
   - Once a few days later

3. **Test restore**:
   - Actually open files from backup
   - Don't just trust verification

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + O` | Browse Source |
| `Cmd/Ctrl + D` | Browse Destination |
| `Cmd/Ctrl + A` | Analyze |
| `Cmd/Ctrl + R` | Start Copy |
| `Cmd/Ctrl + P` | Pause/Resume |
| `Cmd/Ctrl + V` | Verify |
| `Cmd/Ctrl + L` | Clear Log |
| `Cmd/Ctrl + Q` | Quit |

## Configuration File

Location: `~/.intelligent_copier_config.json`

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
  },
  "window_geometry": "1000x750",
  "recent_paths": [
    "/Volumes/MyDrive",
    "/Users/me/Documents"
  ]
}
```

Edit this file to set default preferences.

## Log Files

- **Application log**: `~/intelligent_copier_*.log`
- **Session state**: `~/.intelligent_copier_session.json`
- **Config**: `~/.intelligent_copier_config.json`

View logs:
```bash
# View latest log
tail -f ~/intelligent_copier_*.log

# Search for errors
grep ERROR ~/intelligent_copier_*.log
```
