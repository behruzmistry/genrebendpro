# Contributing to GenreBend Pro

Thank you for your interest in contributing to GenreBend Pro! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/genrebend-pro.git
   cd genrebend-pro
   ```
3. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Development Setup

1. **Create a `.env` file** with your API keys:
   ```env
   LASTFM_API_KEY=your_lastfm_api_key
   MUSICBRAINZ_USER_AGENT=GenreBendPro/1.0
   ```

2. **Test your setup**:
   ```bash
   python main.py --analyze
   ```

## 🔄 Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test them thoroughly

3. **Run tests** (if available):
   ```bash
   python -m pytest tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

## 📝 Pull Request Process

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference any related issues
   - Include screenshots if UI changes

3. **Wait for review** and address any feedback

## 📋 Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to new functions and classes
- Keep functions focused and small
- Add type hints where appropriate

## 🎯 Areas for Contribution

- **Bug fixes**: Report and fix bugs
- **New features**: Add new music research sources or analysis methods
- **Documentation**: Improve README, add examples, write tutorials
- **Testing**: Add unit tests or integration tests
- **Performance**: Optimize API calls or processing speed
- **UI/UX**: Improve command-line interface or add GUI

## 🐛 Reporting Issues

When reporting issues, please include:

- **Description**: Clear description of the problem
- **Steps to reproduce**: How to reproduce the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Logs**: Relevant log output (remove sensitive data)

## 🔐 API Keys and Security

- **Never commit API keys** to the repository
- Use `.env` files for local development
- Use GitHub Secrets for CI/CD
- Be mindful of API rate limits

## ❓ Questions?

- Open an issue for questions
- Check existing issues first
- Be respectful and constructive

Thank you for contributing to GenreBend Pro! 🎵