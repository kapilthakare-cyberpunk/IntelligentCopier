# Copy Session Status - 2026-04-21

## Session Overview
- **Date:** 2026-04-21
- **Session ID:** 20260421_164751
- **Source:** /Volumes/SanDisk Extreme SSD/SanDisk SSD KT Data
- **Destination:** /Volumes/WESTERNDIGI/SanDisk SSD KT Data

## Progress Summary
| Metric | Value |
|--------|-------|
| Source Size | 305 GB |
| Destination Size | 117 GB |
| Files on Source | 384,192 |
| Files on Destination | 54,516 |
| Percentage Complete | ~38% |
| Time Elapsed | ~4 hours 17 minutes |
| Status | PAUSED - Resume Tomorrow |

## Incomplete Folders
The following folders are partially copied and need to be resumed:

| Folder | Source Size | Destination Size | Status |
|--------|-------------|------------------|--------|
| Drive GoogleTakeout 1 Dec 2021 | 145 GB | 111 GB | ⚠️ 34 GB remaining |
| GoogleDrive Backup Kapil | 44 GB | 16 MB | ❌ Needs restart |
| Ganesh visarjan 2014 | 205 MB | 128 KB | ❌ Needs restart |

## Resume Command
To resume the copy tomorrow, run:

```bash
rsync -av --stats --progress \
  --exclude '.DocumentRevisions-V100' \
  --exclude '.fseventsd' \
  --exclude '.Spotlight-V100' \
  --exclude '.TemporaryItems' \
  --exclude '.Trashes' \
  --exclude '.DS_Store' \
  --exclude '._*' \
  --max-size=4095M \
  "/Volumes/SanDisk Extreme SSD/SanDisk SSD KT Data/" \
  "/Volumes/WESTERNDIGI/SanDisk SSD KT Data/"
```

## Verification Results
- ✅ All 66 top-level folders exist on destination
- ⚠️ Large folders incomplete - do not delete from source yet
- ⚠️ Estimated 4-5 hours remaining for full completion

## Notes
- Copy was safely paused using SIGTERM (graceful termination)
- Resume is safe - rsync will skip already-copied files
- DO NOT delete from SSD until copy is 100% complete and verified

---
Last Updated: 2026-04-21 22:43
