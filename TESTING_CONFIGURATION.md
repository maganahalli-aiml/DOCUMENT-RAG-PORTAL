# Testing Configuration for Document RAG Portal CI/CD

## Overview

This document outlines the comprehensive testing strategy implemented in the CI/CD pipeline for the Document RAG Portal. The pipeline includes both pre-commit and post-commit validation to ensure code quality and reliability.

## Testing Stages

### 1. Pre-commit Validation
**Triggers**: Before each commit (local) and on push/PR (GitHub Actions)

**Checks performed**:
- Code formatting (Black)
- Import sorting (isort)
- Linting (flake8)
- Quick unit tests
- Security scanning for sensitive data

**Files involved**:
- `.git/hooks/pre-commit` - Local pre-commit hook
- `.github/workflows/ci.yaml` - CI pre-commit job

### 2. Post-commit Tests
**Triggers**: After commits (local) and on push/PR (GitHub Actions)

**Test categories**:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component interaction testing
- **API Tests**: Endpoint and functionality testing
- **Performance Tests**: Cache and pipeline performance

**Test matrix**:
```yaml
strategy:
  matrix:
    test-group: [unit, integration, api, performance]
```

### 3. RAG Quality Evaluation
**Triggers**: After successful post-commit tests

**Evaluations**:
- RAG response quality metrics
- Document analysis accuracy
- Conversational flow testing
- Performance benchmarks

### 4. Security and Quality Scans
**Triggers**: Parallel with post-commit tests

**Scans**:
- Security vulnerabilities (Bandit)
- Dependency vulnerabilities (Safety)
- Code quality metrics

### 5. Deployment Readiness
**Triggers**: On master/main branch after all tests pass

**Validations**:
- Docker build verification
- Final deployment checks
- Release readiness confirmation

## Test Files Structure

```
tests/
├── __init__.py
├── test_routes.py           # API endpoint tests
└── test_unit_cases.py       # Unit test cases

# Root level test files
├── test_api.py              # API functionality tests
├── test_chat_api.py         # Chat API tests
├── test_cache_performance.py # Cache performance tests
├── test_pipeline.py         # Pipeline tests
├── document_analysis_test.py # Document analysis tests
├── conversational_rag_test.py # Conversational RAG tests
├── document_compare_test.py  # Document comparison tests
└── multidocument_conversational_rag.test.py # Multi-doc tests
```

## Local Development Setup

### Install Pre-commit Hooks
```bash
# Run the setup script
./setup-hooks.sh
```

### Manual Hook Installation
```bash
# Copy pre-commit hook
cp .git/hooks/pre-commit.example .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Required Dependencies
```bash
pip install pytest pytest-cov pytest-mock pytest-xdist
pip install flake8 black isort bandit safety
pip install deepeval  # For RAG evaluation
```

## CI/CD Workflow Triggers

### Automatic Triggers
- **Push** to master, main, ragEnhancement, develop branches
- **Pull Request** to master, main, ragEnhancement branches
- **Manual dispatch** via GitHub Actions UI

### Conditional Execution
- Tests only run if relevant files (.py, .yml, .yaml, .json, .md) are changed
- Deployment readiness check only runs on master/main branches

## Environment Variables

### GitHub Actions Secrets
```yaml
# Required for API testing (set in repository secrets)
GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Test Environment
```yaml
ENVIRONMENT: test
PYTHONPATH: ${{ github.workspace }}
CACHE_KEY_PREFIX: pip-deps
PYTHON_VERSION: '3.10'
```

## Test Commands Reference

### Local Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_unit_cases.py -v       # Unit tests
pytest tests/test_routes.py -v           # API tests
python document_analysis_test.py         # Document analysis
python conversational_rag_test.py        # Conversational RAG
python test_cache_performance.py         # Performance tests

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Pre-commit Validation
```bash
# Run pre-commit checks manually
.git/hooks/pre-commit

# Run individual checks
black --check .                 # Format check
isort --check-only .            # Import sorting
flake8 . --select=E9,F63,F7,F82 # Linting
```

### CI/CD Commands
```bash
# Trigger workflow manually
gh workflow run ci.yaml

# View workflow status
gh workflow view ci.yaml

# Download artifacts
gh run download --name rag-evaluation-results
gh run download --name security-reports
```

## Quality Gates

### Pre-commit Gates
- ✅ Code formatting passes
- ✅ Import sorting correct
- ✅ No critical linting errors
- ✅ Quick unit tests pass
- ✅ No obvious sensitive data

### Post-commit Gates
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ API tests pass
- ✅ Performance tests pass
- ✅ Security scan clean
- ✅ RAG evaluation meets thresholds

### Deployment Gates
- ✅ All previous gates passed
- ✅ Docker build successful
- ✅ Branch is master/main
- ✅ No blocking issues detected

## Troubleshooting

### Common Issues

1. **Pre-commit hook fails**
   ```bash
   # Skip hook temporarily
   git commit --no-verify -m "message"
   
   # Fix formatting
   black .
   isort .
   ```

2. **Tests fail in CI but pass locally**
   ```bash
   # Check environment differences
   env | grep -E "(PYTHON|PATH)"
   
   # Run in isolation
   python -m pytest tests/ --tb=long
   ```

3. **Docker build fails**
   ```bash
   # Test locally
   docker build -t test-build .
   docker run --rm test-build python --version
   ```

### Debug Commands
```bash
# View hook logs
cat .git/hooks/pre-commit

# Check CI logs
gh run list --workflow=ci.yaml
gh run view <run-id>

# Test specific components
python -c "import pytest; pytest.main(['-v', 'tests/'])"
```

## Performance Considerations

- **Parallel Execution**: Tests run in parallel using pytest-xdist
- **Caching**: Dependencies cached between runs
- **Conditional Execution**: Tests only run when relevant files change
- **Matrix Strategy**: Test groups run in parallel for faster feedback

## Security Considerations

- **Secret Management**: API keys stored in GitHub Secrets
- **Vulnerability Scanning**: Automated dependency and code security scans
- **Sensitive Data Detection**: Pre-commit hooks check for exposed secrets
- **Isolated Testing**: Test environment isolated from production

---

**Note**: This testing configuration ensures high code quality and reliability while maintaining developer productivity through efficient, automated validation processes.
