#!/usr/bin/env bash
# Lint code using appropriate linters for the language
# Supports: Python (flake8, pylint), JavaScript/TypeScript (eslint), Go (golint)

set -euo pipefail

VERBOSE=false

log_info() { echo "[INFO] $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

detect_language() {
    local file="$1"
    case "${file##*.}" in
        py) echo "python" ;;
        js|jsx|ts|tsx) echo "javascript" ;;
        go) echo "go" ;;
        *) echo "unknown" ;;
    esac
}

lint_python() {
    local target="$1"
    log_info "Linting Python code: $target"

    if command -v flake8 &> /dev/null; then
        flake8 "$target" --max-line-length=100 --extend-ignore=E203,W503
    elif command -v pylint &> /dev/null; then
        pylint "$target"
    else
        log_error "No Python linter found (install flake8 or pylint)"
        return 1
    fi
}

lint_javascript() {
    local target="$1"
    log_info "Linting JavaScript/TypeScript: $target"

    if command -v npx &> /dev/null && npx eslint --version &> /dev/null; then
        npx eslint "$target"
    else
        log_error "eslint not found (install with: npm install eslint)"
        return 1
    fi
}

lint_go() {
    local target="$1"
    log_info "Linting Go code: $target"

    if command -v golint &> /dev/null; then
        golint "$target"
    elif command -v go &> /dev/null; then
        go vet "$target"
    else
        log_error "No Go linter found"
        return 1
    fi
}

main() {
    local target="${1:-.}"

    if [[ -f "$target" ]]; then
        lang=$(detect_language "$target")
    elif [[ -d "$target" ]]; then
        # For directories, detect from first file
        first_file=$(find "$target" -type f \( -name "*.py" -o -name "*.js" -o -name "*.go" \) | head -1)
        lang=$(detect_language "$first_file")
    else
        log_error "Target not found: $target"
        exit 1
    fi

    case "$lang" in
        python) lint_python "$target" ;;
        javascript) lint_javascript "$target" ;;
        go) lint_go "$target" ;;
        *) log_error "Unsupported language"; exit 1 ;;
    esac
}

main "$@"
