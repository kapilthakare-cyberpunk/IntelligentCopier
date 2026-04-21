# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Windows native support
- Cloud storage integration (S3, Google Drive)
- Scheduling and automation features
- Checksum verification (SHA-256)
- Bandwidth throttling
- Multi-threaded copying
- Dark mode theme
- Internationalization support

## [1.0.0] - 2026-04-21

### Added
- Initial release of Intelligent File Copier
- GUI interface built with tkinter
- Resume capability using rsync
- Dry run mode for previewing copies
- Real-time progress tracking with speed and ETA
- Smart verification system
- Duplicate handling with multiple strategies (skip, overwrite, rename, review)
- Session persistence for interrupted copies
- System file exclusion (.DS_Store, Spotlight, etc.)
- Permission preservation during copy
- Detailed logging with timestamps
- Copy report generation
- Configuration persistence
- Cross-platform support (macOS, Linux)
- Keyboard navigation support
- Tooltips for better UX
- Color-coded status indicators

### Technical
- Built with Python 3.7+
- Uses rsync for reliable file transfers
- Threading for non-blocking UI
- Queue-based message passing
- JSON-based configuration storage
- Comprehensive error handling

## [0.9.0] - 2026-04-20

### Beta Release
- Feature-complete beta version
- Testing with various file sizes and types
- Performance optimization
- Bug fixes from alpha testing

## [0.5.0] - 2026-04-15

### Alpha Release
- Initial prototype
- Basic copy functionality
- Simple GUI implementation
- Core rsync integration

---

## Version History Legend

- **MAJOR**: Breaking changes, significant new features
- **MINOR**: New features, enhancements, non-breaking changes
- **PATCH**: Bug fixes, documentation updates

## Contributing Changes

To add a change to the changelog:

1. Add your change under the `[Unreleased]` section
2. Use the appropriate subsection:
   - `### Added` - New features
   - `### Changed` - Changes to existing functionality
   - `### Deprecated` - Soon-to-be removed features
   - `### Removed` - Removed features
   - `### Fixed` - Bug fixes
   - `### Security` - Security improvements

3. When releasing, move the `[Unreleased]` changes to a new version section

## Release Checklist

- [ ] Update version number in source
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed
- [ ] Run all tests
- [ ] Check code quality (linting)
- [ ] Create git tag
- [ ] Push to GitHub
- [ ] Create GitHub release
- [ ] Update documentation site if applicable
