#!/bin/bash

# Test runner script with coverage reporting

set -e

echo "🧪 Starting test environment..."

# Start test databases
docker-compose -f docker-compose.test.yml up -d

# Wait for databases to be ready
echo "⏳ Waiting for test databases..."
sleep 5

# Run tests
echo "🚀 Running tests..."
pytest tests/ \
    --verbose \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-branch \
    "$@"

# Capture exit code
TEST_EXIT_CODE=$?

# Generate coverage badge (optional)
if command -v coverage-badge &> /dev/null; then
    coverage-badge -o coverage.svg -f
fi

# Cleanup
echo "🧹 Cleaning up test environment..."
docker-compose -f docker-compose.test.yml down -v

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed!"
fi

exit $TEST_EXIT_CODE
