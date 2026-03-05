# Code Quality Analysis - Tobacco Situation Monitor

## Executive Summary

This document analyzes the TSM codebase for code quality, performance optimizations, documentation, and best practices. The analysis identifies **4 failing tests**, **multiple deprecation warnings**, and **several areas for improvement**.

## Issues Found

### 1. Critical: Failing Tests (4 failures)

#### 1.1 `test_alert_engine_add_rule` - AlertEngine initialization issue
**Location**: `tests/test_alert_engine.py:170`
**Problem**: Test expects empty rules when creating `AlertEngine([])`, but the constructor uses `DEFAULT_RULES` when no rules are provided.
**Impact**: Test failure, incorrect test expectations
**Fix**: Update test to properly test empty rules initialization

#### 1.2 `test_extract_suspects` - Regex pattern issue
**Location**: `tests/test_entity_extractor.py:77`
**Problem**: Suspect extraction regex captures too much context (e.g., "张某已被" instead of "张某")
**Impact**: Incorrect entity extraction in production
**Fix**: Refine regex patterns to extract only names

#### 1.3 `test_extract_district` - District extraction logic
**Location**: `tests/test_region_extractor.py:43`
**Problem**: District pattern doesn't properly identify districts without province/city context
**Impact**: Missing district-level extraction
**Fix**: Improve district detection logic

#### 1.4 `test_extract_multiple_levels` - Region hierarchy parsing
**Location**: `tests/test_region_extractor.py:54`
**Problem**: City extraction includes suffix from district (e.g., "州市西湖区" instead of "杭州市")
**Impact**: Incorrect region parsing
**Fix**: Better boundary detection in region patterns

### 2. High Priority: Deprecation Warnings

#### 2.1 FastAPI `regex` parameter deprecated
**Locations**: 
- `src/tsm/api/alerts.py:55`
- `src/tsm/api/trends.py:68`
**Warning**: `FastAPIDeprecationWarning: regex has been deprecated, please use pattern instead`
**Impact**: Will break in future FastAPI versions
**Fix**: Replace `regex` with `pattern` parameter

#### 2.2 Python 3.12 datetime adapter deprecated
**Location**: Multiple test files using sqlite3 with datetime
**Warning**: `The default datetime adapter is deprecated as of Python 3.12`
**Impact**: Will break in future Python versions
**Fix**: Use ISO format strings instead of datetime objects

### 3. Code Quality Improvements

#### 3.1 Configuration Management
**Location**: `src/tsm/config.py`
**Issues**:
- Minimal configuration (only `app_name` and `debug`)
- No database path configuration
- No API settings
- No logging configuration
**Recommendation**: Expand settings class with all configurable parameters

#### 3.2 Database Connection Management
**Location**: Multiple files (`src/tsm/db.py`, `src/tsm/services/*.py`)
**Issues**:
- No connection pooling
- Direct sqlite3 connections in multiple places
- No context manager usage
- No error handling for connection failures
**Recommendation**: Implement database connection manager with context managers

#### 3.3 Error Handling
**Location**: Throughout codebase
**Issues**:
- Minimal try/except blocks
- No custom exception classes
- Silent failures in some functions
**Recommendation**: Add custom exceptions and comprehensive error handling

#### 3.4 Type Hints
**Location**: Multiple files
**Issues**:
- Inconsistent type hint usage
- Missing return types in some functions
- No `Optional` for nullable fields
**Recommendation**: Add comprehensive type hints throughout

#### 3.5 Documentation
**Location**: Throughout codebase
**Issues**:
- Missing docstrings in some modules
- Inconsistent docstring format
- No usage examples
- Missing parameter descriptions
**Recommendation**: Standardize docstrings with Google or NumPy style

#### 3.6 Logging
**Location**: Throughout codebase
**Issues**:
- No logging implementation
- No log levels or formatting
- No structured logging
**Recommendation**: Implement Python logging with appropriate levels

#### 3.7 Testing
**Location**: `tests/` directory
**Issues**:
- No integration tests
- Limited edge case coverage
- No performance tests
- No mock objects for external dependencies
**Recommendation**: Expand test coverage with integration and performance tests

### 4. Performance Optimizations

#### 4.1 In-Memory Hash Storage
**Location**: `src/tsm/services/deduper.py`
**Issue**: `_seen_url_hashes` and `_seen_content_hashes` are in-memory sets
**Impact**: Hashes lost on restart, memory growth over time
**Recommendation**: Use database-backed deduplication with TTL

#### 4.2 Database Queries
**Location**: Multiple API endpoints
**Issues**:
- No query optimization
- Missing database indexes
- N+1 query patterns in some places
**Recommendation**: Add indexes and optimize queries

#### 4.3 Crawler Performance
**Location**: `src/tsm/crawler/fetcher.py`
**Issues**:
- No async/await for HTTP requests
- No connection pooling
- No rate limiting
- No retry logic
**Recommendation**: Implement async HTTP client with retries

### 5. Security Considerations

#### 5.1 Input Validation
**Location**: API endpoints
**Issues**:
- Limited input sanitization
- No SQL injection prevention (using parameterized queries helps)
- No rate limiting on endpoints
**Recommendation**: Add input validation middleware

#### 5.2 Sensitive Data
**Location**: Throughout codebase
**Issues**:
- No encryption for sensitive data
- Database file stored in workspace
**Recommendation**: Implement encryption for sensitive fields

### 6. Best Practices

#### 6.1 Project Structure
**Current**: Good separation of concerns (api, services, intel, crawler)
**Recommendation**: Add `exceptions.py`, `logging_config.py`, `database.py`

#### 6.2 Dependency Management
**Current**: Uses `pyproject.toml` with minimal dependencies
**Recommendation**: 
- Pin dependency versions
- Add security scanning (safety, bandit)
- Add pre-commit hooks

#### 6.3 CI/CD
**Current**: No CI/CD configuration visible
**Recommendation**: Add GitHub Actions workflow for testing and linting

#### 6.4 Code Style
**Current**: Generally follows PEP 8
**Recommendation**: Add black, isort, flake8 configuration

## Recommended Actions

### Immediate (Fix failing tests and deprecations)
1. Fix 4 failing tests
2. Replace `regex` with `pattern` in FastAPI endpoints
3. Fix datetime adapter warnings

### Short-term (Code quality)
1. Add comprehensive type hints
2. Implement logging
3. Add error handling
4. Expand configuration

### Medium-term (Performance)
1. Database connection pooling
2. Async HTTP client
3. Query optimization
4. Caching layer

### Long-term (Architecture)
1. CI/CD pipeline
2. Security hardening
3. Performance monitoring
4. Documentation site

## Test Coverage Summary

```
Total tests: 135
Passed: 131
Failed: 4
Coverage: ~85% (estimated)
```

## Files Requiring Changes

1. `src/tsm/intel/alert_engine.py` - Fix initialization logic
2. `src/tsm/intel/entity_extractor.py` - Fix suspect regex patterns
3. `src/tsm/intel/region_extractor.py` - Fix region extraction logic
4. `src/tsm/api/alerts.py` - Replace regex with pattern
5. `src/tsm/api/trends.py` - Replace regex with pattern
6. `tests/test_alert_engine.py` - Fix test expectations
7. `tests/test_entity_extractor.py` - Update test cases
8. `tests/test_region_extractor.py` - Update test cases
