#!/bin/bash

# Setup Pre-commit Hooks for Document RAG Portal
# This script configures Git hooks to run tests before commits

echo "🔧 Setting up pre-commit hooks for Document RAG Portal..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ This is not a Git repository. Please run this script from the project root."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
echo "📝 Installing pre-commit hook..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Document RAG Portal
# This script runs tests and checks before allowing commits

set -e

echo "🔍 Running pre-commit validation..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
if ! python -c "import pytest" &> /dev/null; then
    echo "📦 Installing required testing packages..."
    pip install pytest pytest-cov flake8 black isort
fi

# Run code formatting check
echo "🎨 Checking code formatting..."
if command -v black &> /dev/null; then
    black --check . || {
        echo "❌ Code formatting issues found. Run 'black .' to fix."
        exit 1
    }
fi

# Run import sorting check
echo "📋 Checking import sorting..."
if command -v isort &> /dev/null; then
    isort --check-only . || {
        echo "❌ Import sorting issues found. Run 'isort .' to fix."
        exit 1
    }
fi

# Run linting
echo "🔍 Running code linting..."
if command -v flake8 &> /dev/null; then
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || {
        echo "❌ Linting issues found. Please fix before committing."
        exit 1
    }
fi

# Run quick unit tests
echo "🧪 Running quick unit tests..."
if [ -f "tests/test_unit_cases.py" ]; then
    python -m pytest tests/test_unit_cases.py -v --tb=short || {
        echo "❌ Unit tests failed. Please fix before committing."
        exit 1
    }
fi

# Run API tests if they exist
if [ -f "test_api.py" ]; then
    echo "🌐 Running API tests..."
    python test_api.py || {
        echo "❌ API tests failed. Please fix before committing."
        exit 1
    }
fi

# Check for secrets or sensitive data
echo "🔐 Checking for sensitive data..."
if grep -r -E "(api_key|password|secret|token|credential)" --include="*.py" --include="*.yml" --include="*.yaml" . | grep -v ".env.template" | grep -v "test_" | grep -v "#"; then
    echo "⚠️  WARNING: Potential sensitive data found. Please review."
fi

echo "✅ Pre-commit validation passed!"
echo "🚀 Proceeding with commit..."
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit

# Install post-commit hook for additional validation
echo "📝 Installing post-commit hook..."
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Post-commit hook for Document RAG Portal
# This script runs comprehensive tests after commits

echo "🚀 Running post-commit validation..."

# Run comprehensive test suite
echo "🧪 Running comprehensive test suite..."

# Run all unit tests
if [ -d "tests" ]; then
    python -m pytest tests/ -v
fi

# Run integration tests
if [ -f "multidocument_conversational_rag.test.py" ]; then
    echo "🔗 Running integration tests..."
    python multidocument_conversational_rag.test.py
fi

# Run document analysis tests
if [ -f "document_analysis_test.py" ]; then
    echo "📄 Running document analysis tests..."
    python document_analysis_test.py
fi

# Run conversational RAG tests
if [ -f "conversational_rag_test.py" ]; then
    echo "💬 Running conversational RAG tests..."
    python conversational_rag_test.py
fi

echo "✅ Post-commit validation completed!"
echo "📊 Check the results above for any issues."
EOF

# Make post-commit hook executable
chmod +x .git/hooks/post-commit

# Install pre-push hook for final validation
echo "📝 Installing pre-push hook..."
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook for Document RAG Portal
# This script runs final validation before pushing to remote

echo "🌐 Running pre-push validation..."

# Run full test suite
echo "🧪 Running full test suite before push..."

# Set up test environment
export ENVIRONMENT=test
export PYTHONPATH=$(pwd)

# Run all tests
python -m pytest tests/ -v --tb=short

# Run RAG evaluation if available
if [ -f "run_rag_evaluation_suite.py" ]; then
    echo "📊 Running RAG evaluation suite..."
    python run_rag_evaluation_suite.py --quick-mode
fi

# Check Docker build
echo "🐳 Validating Docker build..."
if [ -f "Dockerfile" ]; then
    docker build -t test-build . > /dev/null 2>&1 || {
        echo "❌ Docker build failed. Please fix before pushing."
        exit 1
    }
    docker rmi test-build > /dev/null 2>&1 || true
fi

echo "✅ Pre-push validation passed!"
echo "🚀 Ready to push to remote repository!"
EOF

# Make pre-push hook executable
chmod +x .git/hooks/pre-push

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "📋 Installed hooks:"
echo "   • pre-commit: Runs tests and checks before each commit"
echo "   • post-commit: Runs comprehensive tests after commits"
echo "   • pre-push: Final validation before pushing to remote"
echo ""
echo "🔧 To disable hooks temporarily:"
echo "   git commit --no-verify"
echo ""
echo "🔧 To run hooks manually:"
echo "   .git/hooks/pre-commit"
echo "   .git/hooks/post-commit"
echo ""
echo "🎯 Your commits will now be automatically validated!"
