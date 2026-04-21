# Contributing to Intelligent File Copier

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

Before creating a bug report, please:
1. Check if the issue already exists in the [issue tracker](https://github.com/kapilthakare-cyberpunk/IntelligentCopier/issues)
2. Use the latest version to see if the issue is already fixed
3. Collect information about the bug (OS version, Python version, error messages)

**Bug Report Template:**
```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.0]
- Version: [e.g., 1.0.0]

**Logs:**
Relevant log output or error messages
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check if the enhancement is already suggested
2. Provide a clear use case
3. Explain why this would be useful

**Enhancement Template:**
```markdown
**Feature Description:**
Clear description of the proposed feature

**Use Case:**
Who would use this and why?

**Proposed Implementation:**
(Optional) Ideas for how to implement

**Additional Context:**
Screenshots, mockups, or references
```

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🏗️ Development Setup

### Prerequisites

- Python 3.7+
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/IntelligentCopier.git
cd IntelligentCopier

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the application
python3 src/intelligent_copier.py
```

### Project Structure

```
IntelligentCopier/
├── src/                      # Source code
│   └── intelligent_copier.py # Main application
├── tests/                    # Test files
├── docs/                     # Documentation
├── assets/                   # Images, icons
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
├── README.md                 # Main documentation
└── CONTRIBUTING.md           # This file
```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names

### Code Quality

```bash
# Run linter
flake8 src/

# Run type checker
mypy src/

# Run tests
pytest tests/
```

### Documentation

- Add docstrings to all functions and classes
- Keep README.md updated
- Comment complex logic
- Update CHANGELOG.md for significant changes

## 🧪 Testing

### Writing Tests

```python
# tests/test_copier.py
import unittest
from src.intelligent_copier import IntelligentCopier

class TestIntelligentCopier(unittest.TestCase):
    def setUp(self):
        # Setup test fixtures
        pass

    def test_analyze_directory(self):
        # Test directory analysis
        pass

    def test_duplicate_detection(self):
        # Test duplicate handling
        pass
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_copier.py::TestIntelligentCopier::test_analyze
```

## 🎨 UI/UX Guidelines

### Design Principles

- Keep the interface clean and intuitive
- Provide clear feedback for all actions
- Use consistent spacing and alignment
- Support keyboard navigation
- Test on different screen resolutions

### Adding New Features

1. Design the user interface first
2. Implement the backend logic
3. Add appropriate logging
4. Update documentation
5. Add tests
6. Update CHANGELOG.md

## 📦 Release Process

1. Update version number in `src/intelligent_copier.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create a GitHub release with notes

## 💬 Communication

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on the code, not the person

### Where to Ask Questions

- **General questions**: GitHub Discussions
- **Bug reports**: GitHub Issues
- **Feature requests**: GitHub Issues with label "enhancement"
- **Security issues**: Email kapil@example.com directly

## 🏆 Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Intelligent File Copier!**
