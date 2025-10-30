#!/usr/bin/env bash
#
# Tool Name: Test Runner
# Purpose: Execute test suites and report results
# Usage: bash run_tests.sh [options] [test_path]
#
# This tool runs tests using the appropriate test framework
# (pytest, jest, go test, etc.) and provides formatted output.

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
VERBOSE=false
COVERAGE=false
OUTPUT_FORMAT="text"
TEST_FRAMEWORK=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] [test_path]

Run tests and report results.

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -c, --coverage          Run with coverage analysis
    -f, --format FORMAT     Output format: text|json|junit (default: text)
    -t, --framework FRAMEWORK  Test framework: pytest|jest|go|unittest
    -m, --match PATTERN     Run only tests matching pattern
    -k, --keyword KEYWORD   Run tests matching keyword
    -x, --exitfirst         Exit on first failure
    -s, --capture=no        Don't capture output (show print statements)

ARGUMENTS:
    test_path              Path to test file or directory (default: tests/)

EXAMPLES:
    $(basename "$0") tests/test_user.py
    $(basename "$0") -c tests/
    $(basename "$0") -k "test_validation" tests/
    $(basename "$0") -x -s tests/test_integration.py

DESCRIPTION:
    Automatically detects and runs tests using the appropriate test framework
    for the project. Supports pytest (Python), jest (JavaScript), go test (Go),
    and unittest (Python).

    Exit codes:
    0 - All tests passed
    1 - Tests failed or error occurred
    2 - No tests found

EOF
}

detect_test_framework() {
    local test_path="$1"

    # Check if framework explicitly specified
    if [[ -n "$TEST_FRAMEWORK" ]]; then
        echo "$TEST_FRAMEWORK"
        return 0
    fi

    # Detect by file extension and project structure
    if [[ -f "pytest.ini" ]] || [[ -f "pyproject.toml" ]] || [[ "$test_path" == *.py ]]; then
        if command -v pytest &> /dev/null; then
            echo "pytest"
            return 0
        fi
        echo "unittest"
        return 0
    fi

    if [[ -f "package.json" ]] || [[ "$test_path" == *.js ]] || [[ "$test_path" == *.ts ]]; then
        echo "jest"
        return 0
    fi

    if [[ -f "go.mod" ]] || [[ "$test_path" == *.go ]]; then
        echo "go"
        return 0
    fi

    # Default to pytest if python files
    if find "${test_path:-tests}" -name "*.py" 2>/dev/null | grep -q .; then
        echo "pytest"
        return 0
    fi

    log_error "Could not detect test framework"
    return 1
}

run_pytest() {
    local test_path="$1"
    local args=()

    [[ "$VERBOSE" == "true" ]] && args+=("-v")
    [[ "$COVERAGE" == "true" ]] && args+=("--cov" "--cov-report=term-missing")
    [[ -n "${MATCH_PATTERN:-}" ]] && args+=("-k" "$MATCH_PATTERN")
    [[ "${EXIT_FIRST:-false}" == "true" ]] && args+=("-x")
    [[ "${NO_CAPTURE:-false}" == "true" ]] && args+=("-s")

    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        args+=("--json-report" "--json-report-file=/dev/stdout")
    elif [[ "$OUTPUT_FORMAT" == "junit" ]]; then
        args+=("--junit-xml=/dev/stdout")
    fi

    log_info "Running pytest: pytest ${args[*]} $test_path"

    if pytest "${args[@]}" "$test_path"; then
        log_success "All tests passed"
        return 0
    else
        local exit_code=$?
        if [[ $exit_code -eq 5 ]]; then
            log_warn "No tests found"
            return 2
        else
            log_error "Tests failed"
            return 1
        fi
    fi
}

run_unittest() {
    local test_path="$1"

    log_info "Running unittest: python -m unittest discover"

    local args=("-v")
    [[ -n "${MATCH_PATTERN:-}" ]] && args+=("-k" "$MATCH_PATTERN")

    if python -m unittest discover "${args[@]}" -s "$test_path"; then
        log_success "All tests passed"
        return 0
    else
        log_error "Tests failed"
        return 1
    fi
}

run_jest() {
    local test_path="$1"
    local args=()

    [[ "$VERBOSE" == "true" ]] && args+=("--verbose")
    [[ "$COVERAGE" == "true" ]] && args+=("--coverage")
    [[ -n "${MATCH_PATTERN:-}" ]] && args+=("-t" "$MATCH_PATTERN")
    [[ "$OUTPUT_FORMAT" == "json" ]] && args+=("--json")

    log_info "Running jest: jest ${args[*]} $test_path"

    if npx jest "${args[@]}" "$test_path"; then
        log_success "All tests passed"
        return 0
    else
        log_error "Tests failed"
        return 1
    fi
}

run_go_test() {
    local test_path="$1"
    local args=()

    [[ "$VERBOSE" == "true" ]] && args+=("-v")
    [[ "$COVERAGE" == "true" ]] && args+=("-cover" "-coverprofile=coverage.out")
    [[ -n "${MATCH_PATTERN:-}" ]] && args+=("-run" "$MATCH_PATTERN")
    [[ "$OUTPUT_FORMAT" == "json" ]] && args+=("-json")

    log_info "Running go test: go test ${args[*]} $test_path"

    if go test "${args[@]}" "$test_path"; then
        log_success "All tests passed"
        return 0
    else
        log_error "Tests failed"
        return 1
    fi
}

validate_dependencies() {
    local framework="$1"

    case "$framework" in
        pytest)
            if ! command -v pytest &> /dev/null; then
                log_error "pytest not found. Install with: pip install pytest"
                return 1
            fi
            ;;
        jest)
            if ! command -v npx &> /dev/null; then
                log_error "npx not found. Install Node.js and npm"
                return 1
            fi
            if ! npx jest --version &> /dev/null; then
                log_error "jest not found. Install with: npm install --save-dev jest"
                return 1
            fi
            ;;
        go)
            if ! command -v go &> /dev/null; then
                log_error "go not found. Install Go from https://golang.org/dl/"
                return 1
            fi
            ;;
        unittest)
            if ! python -c "import unittest" &> /dev/null; then
                log_error "unittest module not found (should be in Python stdlib)"
                return 1
            fi
            ;;
        *)
            log_error "Unknown framework: $framework"
            return 1
            ;;
    esac

    return 0
}

parse_arguments() {
    local test_path="tests"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--coverage)
                COVERAGE=true
                shift
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -t|--framework)
                TEST_FRAMEWORK="$2"
                shift 2
                ;;
            -m|--match|-k|--keyword)
                MATCH_PATTERN="$2"
                shift 2
                ;;
            -x|--exitfirst)
                EXIT_FIRST=true
                shift
                ;;
            -s|--capture=no)
                NO_CAPTURE=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                test_path="$1"
                shift
                ;;
        esac
    done

    export TEST_PATH="$test_path"
}

main() {
    parse_arguments "$@"

    local test_path="${TEST_PATH:-tests}"

    # Validate test path exists
    if [[ ! -e "$test_path" ]]; then
        log_error "Test path not found: $test_path"
        exit 1
    fi

    # Detect test framework
    local framework
    if ! framework=$(detect_test_framework "$test_path"); then
        exit 1
    fi

    log_info "Detected test framework: $framework"

    # Validate dependencies
    if ! validate_dependencies "$framework"; then
        exit 1
    fi

    # Run tests
    case "$framework" in
        pytest)
            run_pytest "$test_path"
            ;;
        unittest)
            run_unittest "$test_path"
            ;;
        jest)
            run_jest "$test_path"
            ;;
        go)
            run_go_test "$test_path"
            ;;
        *)
            log_error "Unsupported framework: $framework"
            exit 1
            ;;
    esac
}

trap_sigint() {
    log_warn "Tests cancelled by user"
    exit 130
}

trap trap_sigint SIGINT

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
