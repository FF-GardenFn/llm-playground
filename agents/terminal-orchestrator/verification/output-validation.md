# Output Validation

**Purpose**: Verify agent outputs are complete, well-formed, and ready for merge before integration.

**When to Use**: After agent execution completes (Phase 3: Output Verification).

**Gate**: Cannot proceed to merge with invalid outputs.

---

## Validation Pipeline

```
Agent Execution Complete
    ↓
1. Capture outputs (files, logs, exit code)
    ↓
2. Schema validation (expected files exist, correct format)
    ↓
3. Completeness check (all required outputs present)
    ↓
4. Format validation (parseable, well-formed)
    ↓
5. Success criteria (custom checks per agent type)
    ↓
6. Corruption detection (file integrity, malformed data)
    ↓
Valid outputs → Proceed to merge
Invalid outputs → Report error, halt execution
```

---

## 1. Output Capture

### File System Outputs

**Expected locations**:
```
/tmp/orchestration/<execution_id>/outputs/<agent_name>/
├── output.ctxp          # Required: .ctxpack with semantic graph
├── <agent-specific>     # Agent-specific outputs
└── metadata.json        # Required: Output metadata
```

**Capture process**:
1. List all files in output directory: `ls -R outputs/<agent_name>/`
2. Compute file checksums: `sha256sum outputs/<agent_name>/*`
3. Record file sizes: `du -sh outputs/<agent_name>/*`
4. Verify no empty files: `find outputs/<agent_name>/ -type f -empty`

**Example**:
```bash
# code-generator outputs
outputs/code-generator/
├── output.ctxp          # 2.4 MB, sha256: abc123...
├── code/                # Directory with implementation
│   ├── auth.py          # 1.2 KB
│   └── models.py        # 0.8 KB
├── tests/               # Directory with tests
│   └── test_auth.py     # 1.5 KB
└── metadata.json        # 0.3 KB
```

---

### Log Outputs

**Expected locations**:
```
/tmp/orchestration/<execution_id>/logs/<agent_name>/
├── stdout.log           # Standard output from agent
├── stderr.log           # Standard error from agent
└── execution.log        # Terminal Orchestrator's execution log
```

**Capture process**:
1. Read last 100 lines of stdout: `tail -100 stdout.log`
2. Check for error patterns in stderr: `grep -E "ERROR|CRITICAL|Exception" stderr.log`
3. Verify logs are not empty: `[ -s stdout.log ] && [ -s stderr.log ]`

---

### Exit Code

**Check**:
```bash
# Retrieve exit code from tmux session
tmux_exit_code=$(tmux list-panes -t <session-name> -F "#{pane_dead_status}")

# Validate
if [ "$tmux_exit_code" -ne 0 ]; then
    echo "Agent failed with exit code $tmux_exit_code"
fi
```

**Expected**: Exit code 0 for success, non-zero for failure

---

## 2. Schema Validation

### Required Files Check

**Per-agent schema** (from execution request):
```json
{
  "agent_name": "code-generator",
  "required_outputs": [
    {
      "path": "output.ctxp",
      "type": "file",
      "required": true
    },
    {
      "path": "code/",
      "type": "directory",
      "required": true
    },
    {
      "path": "tests/",
      "type": "directory",
      "required": true
    },
    {
      "path": "metadata.json",
      "type": "file",
      "required": true
    }
  ]
}
```

**Validation**:
```python
def validate_schema(agent_name, outputs_dir, required_outputs):
    missing = []
    for output_spec in required_outputs:
        path = os.path.join(outputs_dir, output_spec["path"])

        if output_spec["type"] == "file":
            if not os.path.isfile(path):
                missing.append(f"File missing: {output_spec['path']}")

        elif output_spec["type"] == "directory":
            if not os.path.isdir(path):
                missing.append(f"Directory missing: {output_spec['path']}")

    if missing:
        raise ValidationError(f"Schema validation failed for {agent_name}: {missing}")
```

---

### Metadata Validation

**metadata.json format**:
```json
{
  "agent_name": "code-generator",
  "execution_id": "exec-20251030-1430-abc123",
  "start_time": "2025-10-30T14:30:05Z",
  "end_time": "2025-10-30T14:42:18Z",
  "duration_seconds": 733,
  "outputs": {
    "code": "code/",
    "tests": "tests/",
    "ctxpack": "output.ctxp"
  },
  "metrics": {
    "lines_of_code": 1247,
    "test_count": 42,
    "files_created": 15
  },
  "success": true
}
```

**Validation**:
```python
def validate_metadata(metadata_path):
    with open(metadata_path) as f:
        metadata = json.load(f)

    # Required fields
    required_fields = ["agent_name", "execution_id", "outputs", "success"]
    for field in required_fields:
        if field not in metadata:
            raise ValidationError(f"Missing required field: {field}")

    # Validate timestamps
    if "start_time" in metadata and "end_time" in metadata:
        start = datetime.fromisoformat(metadata["start_time"])
        end = datetime.fromisoformat(metadata["end_time"])
        if end <= start:
            raise ValidationError(f"end_time must be after start_time")

    # Validate outputs exist
    for output_name, output_path in metadata["outputs"].items():
        full_path = os.path.join(os.path.dirname(metadata_path), output_path)
        if not os.path.exists(full_path):
            raise ValidationError(f"Output file missing: {output_path}")
```

---

## 3. Completeness Check

### Output Size Validation

**Prevent empty or truncated files**:
```python
def validate_completeness(outputs_dir):
    issues = []

    # Check for empty files (likely incomplete)
    empty_files = []
    for root, dirs, files in os.walk(outputs_dir):
        for file in files:
            path = os.path.join(root, file)
            if os.path.getsize(path) == 0:
                empty_files.append(path)

    if empty_files:
        issues.append(f"Empty files detected: {empty_files}")

    # Check .ctxpack minimum size (>1KB, usually MB)
    ctxpack_path = os.path.join(outputs_dir, "output.ctxp")
    if os.path.exists(ctxpack_path):
        size = os.path.getsize(ctxpack_path)
        if size < 1024:  # Less than 1KB is suspicious
            issues.append(f".ctxpack too small: {size} bytes (expected >1KB)")

    if issues:
        raise ValidationError(f"Completeness validation failed: {issues}")
```

---

### Expected Count Validation

**If agent specifies expected counts**:
```json
{
  "expected_outputs": {
    "code_files": {"min": 1, "max": 50},
    "test_files": {"min": 1, "max": 100}
  }
}
```

**Validation**:
```python
def validate_counts(outputs_dir, expected_outputs):
    for output_type, bounds in expected_outputs.items():
        if output_type == "code_files":
            count = len(glob.glob(f"{outputs_dir}/code/**/*.py", recursive=True))
        elif output_type == "test_files":
            count = len(glob.glob(f"{outputs_dir}/tests/**/*.py", recursive=True))

        if count < bounds["min"]:
            raise ValidationError(f"{output_type} count {count} < minimum {bounds['min']}")
        if count > bounds["max"]:
            raise ValidationError(f"{output_type} count {count} > maximum {bounds['max']}")
```

---

## 4. Format Validation

### .ctxpack Format Validation

**Validate JSON structure**:
```python
import json

def validate_ctxpack(ctxpack_path):
    try:
        with open(ctxpack_path) as f:
            ctxpack = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f".ctxpack is not valid JSON: {e}")

    # Required top-level keys
    required_keys = ["nodes", "edges", "metadata"]
    for key in required_keys:
        if key not in ctxpack:
            raise ValidationError(f".ctxpack missing required key: {key}")

    # Validate nodes
    if not isinstance(ctxpack["nodes"], list):
        raise ValidationError(".ctxpack 'nodes' must be a list")

    # Validate edges
    if not isinstance(ctxpack["edges"], list):
        raise ValidationError(".ctxpack 'edges' must be a list")

    # Validate metadata
    if not isinstance(ctxpack["metadata"], dict):
        raise ValidationError(".ctxpack 'metadata' must be a dict")
```

**Validate semantic graph structure**:
```python
def validate_graph_structure(ctxpack):
    # Check node IDs are unique
    node_ids = [node["id"] for node in ctxpack["nodes"]]
    if len(node_ids) != len(set(node_ids)):
        raise ValidationError("Duplicate node IDs in .ctxpack")

    # Check edge references valid nodes
    node_id_set = set(node_ids)
    for edge in ctxpack["edges"]:
        if edge["source"] not in node_id_set:
            raise ValidationError(f"Edge references non-existent source node: {edge['source']}")
        if edge["target"] not in node_id_set:
            raise ValidationError(f"Edge references non-existent target node: {edge['target']}")
```

---

### Code Format Validation

**Python syntax check**:
```python
import ast

def validate_python_file(file_path):
    with open(file_path) as f:
        code = f.read()

    try:
        ast.parse(code)
    except SyntaxError as e:
        raise ValidationError(f"Python syntax error in {file_path}: {e}")
```

**Linter check** (if specified in success criteria):
```bash
# Run pylint on code files
pylint outputs/code-generator/code/*.py --errors-only

# Check exit code
if [ $? -ne 0 ]; then
    echo "Linting failed - code has errors"
fi
```

---

### Markdown Format Validation

**Check for valid markdown**:
```python
def validate_markdown(file_path):
    with open(file_path) as f:
        content = f.read()

    # Basic checks
    if not content.strip():
        raise ValidationError(f"Markdown file is empty: {file_path}")

    # Check for unclosed code blocks
    if content.count("```") % 2 != 0:
        raise ValidationError(f"Unclosed code block in {file_path}")
```

---

## 5. Success Criteria Validation

### Custom Checks Per Agent

**From execution request**:
```json
{
  "success_criteria": {
    "tests_pass": true,
    "no_lint_errors": true,
    "coverage": 80
  }
}
```

**Validation**:
```python
def validate_success_criteria(outputs_dir, success_criteria):
    results = {}

    # Test execution
    if success_criteria.get("tests_pass"):
        pytest_result = subprocess.run(
            ["pytest", f"{outputs_dir}/tests", "--tb=short"],
            capture_output=True
        )
        results["tests_pass"] = (pytest_result.returncode == 0)

    # Linting
    if success_criteria.get("no_lint_errors"):
        pylint_result = subprocess.run(
            ["pylint", f"{outputs_dir}/code", "--errors-only"],
            capture_output=True
        )
        results["no_lint_errors"] = (pylint_result.returncode == 0)

    # Coverage
    if "coverage" in success_criteria:
        coverage_result = subprocess.run(
            ["pytest", f"{outputs_dir}/tests", "--cov", f"{outputs_dir}/code", "--cov-report=json"],
            capture_output=True
        )
        with open("coverage.json") as f:
            coverage_data = json.load(f)
        actual_coverage = coverage_data["totals"]["percent_covered"]
        results["coverage"] = (actual_coverage >= success_criteria["coverage"])

    # Check all criteria met
    failed_criteria = [k for k, v in results.items() if not v]
    if failed_criteria:
        raise ValidationError(f"Success criteria not met: {failed_criteria}")
```

---

### Agent-Specific Validators

**code-generator**:
```python
def validate_code_generator_output(outputs_dir):
    # Check tests exist and pass
    test_files = glob.glob(f"{outputs_dir}/tests/**/test_*.py", recursive=True)
    if not test_files:
        raise ValidationError("No test files found")

    # Run tests
    result = subprocess.run(["pytest", f"{outputs_dir}/tests"], capture_output=True)
    if result.returncode != 0:
        raise ValidationError(f"Tests failed:\n{result.stdout.decode()}")
```

**code-reviewer**:
```python
def validate_code_reviewer_output(outputs_dir):
    # Check review file exists
    review_path = f"{outputs_dir}/review.md"
    if not os.path.exists(review_path):
        raise ValidationError("Review file missing")

    # Check review has required sections
    with open(review_path) as f:
        content = f.read()

    required_sections = ["## Security Issues", "## Code Quality", "## Recommendations"]
    for section in required_sections:
        if section not in content:
            raise ValidationError(f"Review missing required section: {section}")
```

**data-profiler**:
```python
def validate_data_profiler_output(outputs_dir):
    # Check profiling report exists
    report_path = f"{outputs_dir}/data_profile.json"
    if not os.path.exists(report_path):
        raise ValidationError("Data profile report missing")

    # Validate report structure
    with open(report_path) as f:
        profile = json.load(f)

    required_keys = ["dataset_name", "row_count", "column_count", "issues"]
    for key in required_keys:
        if key not in profile:
            raise ValidationError(f"Data profile missing required key: {key}")
```

---

## 6. Corruption Detection

### File Integrity Check

**Verify file hashes** (if provided in metadata):
```python
import hashlib

def verify_file_integrity(file_path, expected_hash):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    actual_hash = sha256.hexdigest()
    if actual_hash != expected_hash:
        raise ValidationError(f"File corruption detected: {file_path} (hash mismatch)")
```

---

### Malformed Data Detection

**Check for common corruption patterns**:
```python
def detect_corruption(file_path):
    with open(file_path, "rb") as f:
        content = f.read()

    # Check for null bytes (usually corruption)
    if b'\x00' in content:
        raise ValidationError(f"Null bytes detected in {file_path} (likely corrupted)")

    # Check for truncation markers
    if content.endswith(b"...TRUNCATED"):
        raise ValidationError(f"File appears truncated: {file_path}")

    # Check for incomplete JSON
    if file_path.endswith(".json"):
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Malformed JSON in {file_path}: {e}")
```

---

## Validation Report

### Output Format

```json
{
  "agent_name": "code-generator",
  "validation_timestamp": "2025-10-30T14:42:30Z",
  "status": "valid",
  "checks": [
    {
      "check": "schema_validation",
      "status": "passed",
      "message": "All required files present"
    },
    {
      "check": "completeness",
      "status": "passed",
      "message": "No empty files, .ctxpack size valid"
    },
    {
      "check": "format_validation",
      "status": "passed",
      "message": ".ctxpack is valid JSON, no syntax errors in code"
    },
    {
      "check": "success_criteria",
      "status": "passed",
      "message": "Tests pass (42/42), no lint errors, coverage 85%"
    },
    {
      "check": "corruption_detection",
      "status": "passed",
      "message": "No corruption detected"
    }
  ],
  "errors": [],
  "warnings": [
    {
      "check": "file_size",
      "message": "Large .ctxpack file (2.4 MB) - may impact merge performance"
    }
  ]
}
```

---

## Integration

### Called from Terminal Orchestrator

```python
from terminal_orchestrator.verification import output_validation

# After agent execution completes
try:
    validation_report = output_validation.validate(
        agent_name="code-generator",
        outputs_dir="/tmp/orchestration/outputs/code-generator",
        execution_request=execution_request
    )

    if validation_report["status"] == "valid":
        print("✓ Outputs validated, proceeding to merge")
    else:
        print(f"✗ Validation failed: {validation_report['errors']}")

except ValidationError as e:
    print(f"✗ Validation error: {e}")
    # Mark agent as failed in execution report
```

---

## Summary

**Validation Pipeline**:
1. **Capture**: Collect outputs, logs, exit code
2. **Schema**: Check required files exist
3. **Completeness**: Verify outputs not empty/truncated
4. **Format**: Validate parseable and well-formed
5. **Success Criteria**: Run custom checks per agent
6. **Corruption**: Detect malformed data

**Gate**: Cannot proceed to merge without passing all validation checks

**Output**: Validation report with status, checks, errors, warnings
