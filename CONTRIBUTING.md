# Contributing to LLM-Powered Network Analyzer

Thank you for your interest in contributing to the LLM-Powered Network Analyzer! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

We welcome contributions of all kinds:
- 🐛 Bug reports and fixes
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Test coverage improvements
- 🎨 UI/UX improvements
- 🔧 Performance optimizations

## 🚀 Getting Started

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/LLM-Powered-Network-Analyzer.git
   cd LLM-Powered-Network-Analyzer
   ```

### 2. Set Up Development Environment

Run the automated setup:
```bash
python setup.py
```

Or follow the manual setup in [README.md](README.md#manual-setup-alternative).

### 3. Create a Branch

Create a feature branch for your changes:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

## 📋 Development Guidelines

### Code Style

#### Python (Backend)
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where possible
- Add docstrings to functions and classes
- Maximum line length: 88 characters (Black formatter)

```python
def analyze_packets(packets: List[Dict], baseline: Dict) -> List[Anomaly]:
    """
    Analyze network packets for anomalies.
    
    Args:
        packets: List of parsed packet dictionaries
        baseline: Baseline statistics for comparison
        
    Returns:
        List of detected anomalies
    """
    pass
```

#### TypeScript/Angular (Frontend)
- Follow [Angular Style Guide](https://angular.io/guide/styleguide)
- Use TypeScript strict mode
- Prefer interfaces over classes for data models
- Use meaningful component and service names

```typescript
interface AnalysisResult {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  type: string;
  description: string;
  evidence: Record<string, any>;
}
```

### Testing

#### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

#### Frontend Tests
```bash
cd frontend
ng test
ng e2e  # End-to-end tests
```

### Code Quality Tools

We use several tools to maintain code quality:

#### Python
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

```bash
# Install development dependencies
pip install black isort flake8 mypy pytest

# Format code
black backend/
isort backend/

# Check linting
flake8 backend/
mypy backend/
```

#### TypeScript/Angular
- **ESLint**: Linting
- **Prettier**: Code formatting

```bash
# Install development dependencies
npm install --save-dev eslint prettier

# Format code
npm run lint
npm run format
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Operating system
   - Python version
   - Node.js version
   - Ollama version
   - Browser (for frontend issues)
5. **Log files** or error messages
6. **Sample files** that reproduce the issue (if applicable)

### Bug Report Template

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- Node.js: [e.g., 20.9.0]
- Browser: [e.g., Chrome 119]

## Additional Context
Any other relevant information
```

## ✨ Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** with implementation details
4. **Consider alternatives** and explain why your approach is best
5. **Think about breaking changes** and backward compatibility

### Feature Request Template

```markdown
## Problem Statement
What problem does this feature solve?

## Proposed Solution
Detailed description of the proposed feature

## Alternative Solutions
Other approaches considered

## Implementation Details
Technical details about implementation

## Breaking Changes
Any breaking changes this would introduce
```

## 🔄 Pull Request Process

### Before Submitting

1. **Test your changes** thoroughly
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Run the full test suite**
5. **Check code style** and formatting

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear and descriptive

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
```

## 🏗️ Architecture Guidelines

### Backend Architecture

```
backend/
├── main.py              # FastAPI application entry point
├── api/                 # API route handlers
├── core/                # Core business logic
├── models/              # Data models and schemas
├── services/            # Business logic services
├── utils/               # Utility functions
└── tests/               # Test files
```

### Frontend Architecture

```
frontend/src/app/
├── core/                # Core services and guards
├── shared/              # Shared components and utilities
├── features/            # Feature modules
│   ├── upload/          # File upload feature
│   └── analysis/        # Analysis results feature
└── models/              # TypeScript interfaces
```

### Key Principles

1. **Separation of Concerns**: Keep business logic separate from presentation
2. **Single Responsibility**: Each class/function should have one responsibility
3. **Dependency Injection**: Use DI for testability and flexibility
4. **Error Handling**: Comprehensive error handling with user-friendly messages
5. **Security**: Input validation, sanitization, and secure defaults

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual functions/components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test with large files and datasets

### Test Coverage

Aim for:
- **Backend**: >90% code coverage
- **Frontend**: >80% code coverage
- **Critical paths**: 100% coverage

### Test Data

- Use the test data generators in `backend/tests/`
- Create realistic test scenarios
- Test edge cases and error conditions
- Keep test files small for CI/CD

## 📚 Documentation

### Code Documentation

- **Python**: Use docstrings (Google style)
- **TypeScript**: Use JSDoc comments
- **README files**: For each major component
- **API documentation**: Auto-generated from code

### User Documentation

- **Setup guides**: Clear installation instructions
- **User guides**: Step-by-step usage instructions
- **Troubleshooting**: Common issues and solutions
- **Examples**: Real-world usage examples

## 🚀 Release Process

### Version Numbers

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Create release branch
5. Tag release
6. Update documentation
7. Create GitHub release

## 🤔 Questions?

If you have questions about contributing:

1. Check existing [GitHub Issues](https://github.com/P-Orion/LLM-Powered-Network-Analyzer/issues)
2. Create a new issue with the "question" label
3. Join our discussions in GitHub Discussions

## 📄 Code of Conduct

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated promptly and fairly.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to LLM-Powered Network Analyzer! 🎉