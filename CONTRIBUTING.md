# Contributing to iOps

Thank you for your interest in contributing to iOps! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and constructive in all interactions. We're committed to providing a welcoming and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/iOps.git
   cd iOps
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Making Changes

### Code Style

**Python:**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for function arguments and return values
- Maximum line length: 100 characters
- Use meaningful variable and function names

**TypeScript/JavaScript:**
- Use ESLint configuration provided in the project
- Use Prettier for code formatting
- Use meaningful variable and function names
- Prefer `const` over `let`, avoid `var`

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add short code generation for public reports
fix: Resolve database connection pooling issue
docs: Update API documentation
test: Add tests for usage tracking
refactor: Simplify authentication middleware
```

Use the following prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Build, dependencies, or tooling

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Test both happy paths and error cases

## Pull Request Process

1. **Update your branch** with the latest main:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues (#123)
   - Screenshots for UI changes

4. **Address feedback** from reviewers

5. **Ensure all checks pass**:
   - Tests pass
   - Code style is correct
   - No merge conflicts

## Documentation

- Update README.md if adding new features
- Add docstrings to all functions and classes
- Update API documentation for endpoint changes
- Include examples for complex features

## Reporting Issues

When reporting bugs, please include:

- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python/Node version, etc.)
- Screenshots or error logs if applicable

## Feature Requests

When suggesting features:

- Describe the use case
- Explain the expected behavior
- Provide examples if possible
- Consider backward compatibility

## Project Structure

```
iOps/
├── backend/              # FastAPI backend
│   ├── routers/         # API endpoints
│   ├── utils/           # Utility functions
│   ├── middleware/      # Custom middleware
│   ├── tests/           # Test suite
│   └── models.py        # Database models
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── services/    # API client
│   └── tests/           # Test suite
└── .kiro/specs/         # Feature specifications
```

## Development Workflow

1. **Create a feature branch** from `main`
2. **Make your changes** with clear commits
3. **Write/update tests** for your changes
4. **Update documentation** as needed
5. **Submit a pull request** for review
6. **Address feedback** from reviewers
7. **Merge** once approved

## Performance Considerations

- Optimize database queries with proper indexing
- Use caching for expensive operations
- Implement pagination for large datasets
- Minimize frontend bundle size
- Use lazy loading for components

## Security Guidelines

- Never commit secrets or API keys
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Sanitize output to prevent XSS
- Implement rate limiting for API endpoints
- Use HTTPS in production

## Questions?

- Check existing [GitHub Issues](https://github.com/yourusername/iOps/issues)
- Review [Documentation](README.md)
- Start a [Discussion](https://github.com/yourusername/iOps/discussions)

## License

By contributing to iOps, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to iOps! 🎉
