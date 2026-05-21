#!/bin/bash

# Test Runner Script for Admin Agent
# Runs both backend and frontend tests

set -e

echo "====================================="
echo "Admin Agent - Test Suite Runner"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
COVERAGE=false
WATCH=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --backend)
      BACKEND_ONLY=true
      shift
      ;;
    --frontend)
      FRONTEND_ONLY=true
      shift
      ;;
    --coverage)
      COVERAGE=true
      shift
      ;;
    --watch)
      WATCH=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./run-tests.sh [--backend] [--frontend] [--coverage] [--watch]"
      exit 1
      ;;
  esac
done

# Backend Tests
if [ "$FRONTEND_ONLY" = false ]; then
  echo -e "${YELLOW}Running Backend Tests...${NC}"
  echo "====================================="
  cd backend

  # Check if virtual environment exists
  if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
  fi

  # Activate virtual environment
  source venv/bin/activate || source venv/Scripts/activate

  # Install dependencies
  echo -e "${YELLOW}Installing dependencies...${NC}"
  pip install -q -r requirements.txt
  pip install -q -r requirements-test.txt

  # Run tests
  if [ "$COVERAGE" = true ]; then
    echo -e "${YELLOW}Running tests with coverage...${NC}"
    pytest --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
  elif [ "$WATCH" = true ]; then
    echo -e "${YELLOW}Running tests in watch mode...${NC}"
    pytest-watch
  else
    pytest -v
  fi

  BACKEND_EXIT=$?
  cd ..

  if [ $BACKEND_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Backend tests passed${NC}"
  else
    echo -e "${RED}✗ Backend tests failed${NC}"
  fi
  echo ""
fi

# Frontend Tests
if [ "$BACKEND_ONLY" = false ]; then
  echo -e "${YELLOW}Running Frontend Tests...${NC}"
  echo "====================================="
  cd frontend

  # Install dependencies if needed
  if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
  fi

  # Run tests
  if [ "$COVERAGE" = true ]; then
    echo -e "${YELLOW}Running tests with coverage...${NC}"
    npm test -- --coverage
  elif [ "$WATCH" = true ]; then
    echo -e "${YELLOW}Running tests in watch mode...${NC}"
    npm test -- --watch
  else
    npm test
  fi

  FRONTEND_EXIT=$?
  cd ..

  if [ $FRONTEND_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend tests passed${NC}"
  else
    echo -e "${RED}✗ Frontend tests failed${NC}"
  fi
  echo ""
fi

# Summary
echo "====================================="
echo "Test Summary"
echo "====================================="

if [ "$FRONTEND_ONLY" = false ]; then
  if [ $BACKEND_EXIT -eq 0 ]; then
    echo -e "Backend:  ${GREEN}PASSED${NC}"
  else
    echo -e "Backend:  ${RED}FAILED${NC}"
  fi
fi

if [ "$BACKEND_ONLY" = false ]; then
  if [ $FRONTEND_EXIT -eq 0 ]; then
    echo -e "Frontend: ${GREEN}PASSED${NC}"
  else
    echo -e "Frontend: ${RED}FAILED${NC}"
  fi
fi

echo ""

# Exit with error if any tests failed
if [ "$FRONTEND_ONLY" = false ] && [ $BACKEND_EXIT -ne 0 ]; then
  exit 1
fi

if [ "$BACKEND_ONLY" = false ] && [ $FRONTEND_EXIT -ne 0 ]; then
  exit 1
fi

echo -e "${GREEN}All tests passed!${NC}"
exit 0