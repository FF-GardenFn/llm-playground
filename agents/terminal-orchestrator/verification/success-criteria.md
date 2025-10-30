# Success Criteria

**Purpose**: Define what constitutes successful agent execution beyond basic output validation.

**When to Use**: Part of Phase 3 (Output Verification) after schema and format validation pass.

**Gate**: Agent outputs must meet success criteria before proceeding to merge.

---

## Success Criteria Framework

```
Output Validation (schema, format, completeness)
    ↓
Success Criteria Evaluation
    ├─→ Exit Code Check (0 = success)
    ├─→ Required Outputs Present
    ├─→ Agent-Specific Checks (tests, lint, coverage, etc.)
    └─→ Custom Checks (from execution request)
    ↓
All criteria met → Mark agent as successful
Any criteria failed → Mark agent as failed (even if exit code 0)
```

---

## Universal Success Criteria

### 1. Exit Code Check

**Rule**: Agent process must exit with code 0

**Validation**:
```python
def check_exit_code(agent_execution):
    exit_code = agent_execution["exit_code"]
    if exit_code != 0:
        return False, f"Non-zero exit code: {exit_code}"
    return True, "Exit code 0 (success)"
```

**Exception**: Some agents may define custom success exit codes (e.g., 0 or 42 = success)

---

### 2. Required Outputs Present

**Rule**: All outputs specified in execution request must exist

**Validation**:
```python
def check_required_outputs(outputs_dir, required_outputs):
    missing = []
    for output in required_outputs:
        path = os.path.join(outputs_dir, output)
        if not os.path.exists(path):
            missing.append(output)

    if missing:
        return False, f"Missing required outputs: {missing}"
    return True, "All required outputs present"
```

---

### 3. No Critical Errors in Logs

**Rule**: stderr should not contain CRITICAL or FATAL errors

**Validation**:
```bash
# Check for critical errors
critical_errors=$(grep -E "CRITICAL|FATAL|Traceback" stderr.log | wc -l)

if [ "$critical_errors" -gt 0 ]; then
    echo "FAILED: Critical errors detected in logs"
fi
```

**Note**: Warnings are acceptable, but CRITICAL/FATAL indicate failure

---

## Agent-Specific Success Criteria

### code-generator

**Success Criteria**:
1. **Tests pass**: All generated tests must pass
2. **No lint errors**: Code must pass linting (errors only, warnings OK)
3. **Coverage threshold**: Test coverage ≥ specified threshold (default 80%)
4. **Syntax valid**: All generated code must be syntactically correct

**Validation**:
```python
def validate_code_generator_success(outputs_dir, criteria):
    results = {}

    # 1. Tests pass
    pytest_result = subprocess.run(
        ["pytest", f"{outputs_dir}/tests", "--tb=short", "-v"],
        capture_output=True,
        text=True
    )
    results["tests_pass"] = (pytest_result.returncode == 0)
    if not results["tests_pass"]:
        results["test_failure_reason"] = pytest_result.stdout

    # 2. No lint errors
    pylint_result = subprocess.run(
        ["pylint", f"{outputs_dir}/code", "--errors-only"],
        capture_output=True,
        text=True
    )
    results["no_lint_errors"] = (pylint_result.returncode == 0)
    if not results["no_lint_errors"]:
        results["lint_errors"] = pylint_result.stdout

    # 3. Coverage threshold
    if "coverage" in criteria:
        coverage_result = subprocess.run(
            ["pytest", f"{outputs_dir}/tests",
             "--cov", f"{outputs_dir}/code",
             "--cov-report=json"],
            capture_output=True
        )
        with open("coverage.json") as f:
            coverage_data = json.load(f)
        actual_coverage = coverage_data["totals"]["percent_covered"]
        results["coverage"] = (actual_coverage >= criteria["coverage"])
        results["actual_coverage"] = actual_coverage

    # 4. Syntax valid
    code_files = glob.glob(f"{outputs_dir}/code/**/*.py", recursive=True)
    syntax_errors = []
    for file_path in code_files:
        try:
            with open(file_path) as f:
                ast.parse(f.read())
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
    results["syntax_valid"] = (len(syntax_errors) == 0)
    if syntax_errors:
        results["syntax_errors"] = syntax_errors

    # Check all criteria
    all_passed = all([
        results.get("tests_pass", False),
        results.get("no_lint_errors", False),
        results.get("coverage", True),  # Optional
        results.get("syntax_valid", False)
    ])

    return all_passed, results
```

**Example**:
```json
{
  "success_criteria": {
    "tests_pass": true,
    "no_lint_errors": true,
    "coverage": 80,
    "syntax_valid": true
  }
}
```

---

### code-reviewer

**Success Criteria**:
1. **Review complete**: Review file exists with all required sections
2. **No critical issues**: No unresolved critical security issues
3. **Checklist complete**: Security/quality checklist fully addressed

**Validation**:
```python
def validate_code_reviewer_success(outputs_dir, criteria):
    results = {}

    # 1. Review complete
    review_path = f"{outputs_dir}/review.md"
    results["review_exists"] = os.path.exists(review_path)

    if results["review_exists"]:
        with open(review_path) as f:
            review_content = f.read()

        # Check required sections
        required_sections = [
            "## Security Issues",
            "## Code Quality",
            "## Recommendations"
        ]
        missing_sections = [s for s in required_sections if s not in review_content]
        results["review_complete"] = (len(missing_sections) == 0)
        if missing_sections:
            results["missing_sections"] = missing_sections

        # 2. No critical issues (check for "CRITICAL:" markers)
        critical_count = review_content.count("CRITICAL:")
        results["no_critical_issues"] = (critical_count == 0)
        if critical_count > 0:
            results["critical_issues_count"] = critical_count

        # 3. Checklist complete (check for unchecked items)
        unchecked_items = review_content.count("- [ ]")
        results["checklist_complete"] = (unchecked_items == 0)
        if unchecked_items > 0:
            results["unchecked_items"] = unchecked_items

    else:
        results["review_complete"] = False
        results["no_critical_issues"] = False
        results["checklist_complete"] = False

    all_passed = all([
        results.get("review_exists", False),
        results.get("review_complete", False),
        results.get("no_critical_issues", False) if criteria.get("no_critical_issues") else True,
        results.get("checklist_complete", False) if criteria.get("checklist_complete") else True
    ])

    return all_passed, results
```

**Example**:
```json
{
  "success_criteria": {
    "review_complete": true,
    "no_critical_issues": true,
    "checklist_complete": true
  }
}
```

---

### data-profiler

**Success Criteria**:
1. **Profile complete**: Data profile report exists with required metrics
2. **No critical issues**: No critical data quality issues (target leakage, split contamination)
3. **Issue classification**: All issues classified by priority (Critical/High/Medium/Low)

**Validation**:
```python
def validate_data_profiler_success(outputs_dir, criteria):
    results = {}

    # 1. Profile complete
    profile_path = f"{outputs_dir}/data_profile.json"
    results["profile_exists"] = os.path.exists(profile_path)

    if results["profile_exists"]:
        with open(profile_path) as f:
            profile = json.load(f)

        # Check required metrics
        required_metrics = ["row_count", "column_count", "missing_values", "issues"]
        missing_metrics = [m for m in required_metrics if m not in profile]
        results["profile_complete"] = (len(missing_metrics) == 0)
        if missing_metrics:
            results["missing_metrics"] = missing_metrics

        # 2. No critical issues
        if "issues" in profile:
            critical_issues = [i for i in profile["issues"] if i.get("priority") == "CRITICAL"]
            results["no_critical_issues"] = (len(critical_issues) == 0)
            if critical_issues:
                results["critical_issues"] = [i["description"] for i in critical_issues]
        else:
            results["no_critical_issues"] = True

        # 3. Issue classification
        if "issues" in profile:
            unclassified = [i for i in profile["issues"] if "priority" not in i]
            results["issues_classified"] = (len(unclassified) == 0)
            if unclassified:
                results["unclassified_count"] = len(unclassified)
        else:
            results["issues_classified"] = True

    else:
        results["profile_complete"] = False
        results["no_critical_issues"] = False
        results["issues_classified"] = False

    all_passed = all([
        results.get("profile_exists", False),
        results.get("profile_complete", False),
        results.get("no_critical_issues", False) if criteria.get("no_critical_issues") else True,
        results.get("issues_classified", False) if criteria.get("issues_classified") else True
    ])

    return all_passed, results
```

**Example**:
```json
{
  "success_criteria": {
    "profile_complete": true,
    "no_critical_issues": true,
    "issues_classified": true
  }
}
```

---

### ml-trainer

**Success Criteria**:
1. **Model trained**: Model file exists and is loadable
2. **Metrics recorded**: Training metrics (loss, accuracy) logged
3. **Reproducibility**: Random seeds set, experiment tracked
4. **Production ready**: Passes 24-item production readiness gate

**Validation**:
```python
def validate_ml_trainer_success(outputs_dir, criteria):
    results = {}

    # 1. Model trained
    model_path = f"{outputs_dir}/model.pkl"
    results["model_exists"] = os.path.exists(model_path)

    if results["model_exists"]:
        try:
            import pickle
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            results["model_loadable"] = True
        except Exception as e:
            results["model_loadable"] = False
            results["model_load_error"] = str(e)
    else:
        results["model_loadable"] = False

    # 2. Metrics recorded
    metrics_path = f"{outputs_dir}/metrics.json"
    results["metrics_exist"] = os.path.exists(metrics_path)

    if results["metrics_exist"]:
        with open(metrics_path) as f:
            metrics = json.load(f)
        required_metrics = ["train_loss", "val_loss", "train_accuracy", "val_accuracy"]
        missing_metrics = [m for m in required_metrics if m not in metrics]
        results["metrics_complete"] = (len(missing_metrics) == 0)
    else:
        results["metrics_complete"] = False

    # 3. Reproducibility
    config_path = f"{outputs_dir}/config.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        results["random_seed_set"] = ("random_seed" in config)
        results["experiment_tracked"] = ("experiment_id" in config)
    else:
        results["random_seed_set"] = False
        results["experiment_tracked"] = False

    # 4. Production ready gate (if specified)
    if criteria.get("production_ready"):
        gate_path = f"{outputs_dir}/production_gate.json"
        if os.path.exists(gate_path):
            with open(gate_path) as f:
                gate = json.load(f)
            results["production_ready"] = (gate.get("status") == "passed")
            results["gate_passed_count"] = gate.get("passed_count", 0)
            results["gate_total_count"] = gate.get("total_count", 24)
        else:
            results["production_ready"] = False

    all_passed = all([
        results.get("model_exists", False),
        results.get("model_loadable", False),
        results.get("metrics_complete", False),
        results.get("random_seed_set", False) if criteria.get("reproducibility") else True,
        results.get("production_ready", True)  # Optional, default True if not specified
    ])

    return all_passed, results
```

**Example**:
```json
{
  "success_criteria": {
    "model_trained": true,
    "metrics_recorded": true,
    "reproducibility": true,
    "production_ready": true
  }
}
```

---

### react-architect

**Success Criteria**:
1. **Components created**: React component files exist
2. **Accessibility passed**: Components pass WCAG AA checklist
3. **Performance optimized**: Performance checklist complete
4. **Tests written**: Component tests exist and pass

**Validation**:
```python
def validate_react_architect_success(outputs_dir, criteria):
    results = {}

    # 1. Components created
    component_files = glob.glob(f"{outputs_dir}/components/**/*.tsx", recursive=True)
    results["components_created"] = (len(component_files) > 0)
    results["component_count"] = len(component_files)

    # 2. Accessibility passed
    a11y_report_path = f"{outputs_dir}/accessibility_report.json"
    if os.path.exists(a11y_report_path):
        with open(a11y_report_path) as f:
            a11y_report = json.load(f)
        results["accessibility_passed"] = (a11y_report.get("violations", []) == [])
        results["accessibility_score"] = a11y_report.get("score", 0)
    else:
        results["accessibility_passed"] = False if criteria.get("accessibility_passed") else True

    # 3. Performance optimized
    perf_checklist_path = f"{outputs_dir}/performance_checklist.md"
    if os.path.exists(perf_checklist_path):
        with open(perf_checklist_path) as f:
            checklist = f.read()
        unchecked = checklist.count("- [ ]")
        results["performance_optimized"] = (unchecked == 0)
        results["performance_checks_remaining"] = unchecked
    else:
        results["performance_optimized"] = False if criteria.get("performance_optimized") else True

    # 4. Tests written
    test_files = glob.glob(f"{outputs_dir}/components/**/*.test.tsx", recursive=True)
    results["tests_exist"] = (len(test_files) > 0)
    results["test_count"] = len(test_files)

    if results["tests_exist"]:
        # Run tests
        test_result = subprocess.run(
            ["npm", "test", "--", "--passWithNoTests"],
            cwd=outputs_dir,
            capture_output=True
        )
        results["tests_pass"] = (test_result.returncode == 0)
    else:
        results["tests_pass"] = False

    all_passed = all([
        results.get("components_created", False),
        results.get("accessibility_passed", True),
        results.get("performance_optimized", True),
        results.get("tests_exist", False) if criteria.get("tests_written") else True,
        results.get("tests_pass", False) if criteria.get("tests_pass") else True
    ])

    return all_passed, results
```

**Example**:
```json
{
  "success_criteria": {
    "components_created": true,
    "accessibility_passed": true,
    "performance_optimized": true,
    "tests_written": true,
    "tests_pass": true
  }
}
```

---

## Custom Success Criteria

### Defining Custom Checks

**In execution request**:
```json
{
  "agent_name": "custom-agent",
  "success_criteria": {
    "custom_checks": [
      {
        "name": "file_count",
        "type": "file_count",
        "path": "outputs/*.json",
        "min": 5,
        "max": 10
      },
      {
        "name": "keyword_present",
        "type": "content_check",
        "file": "outputs/report.md",
        "keyword": "RECOMMENDATION",
        "min_occurrences": 1
      },
      {
        "name": "script_execution",
        "type": "script",
        "command": "python validate_output.py",
        "expected_exit_code": 0
      }
    ]
  }
}
```

**Validation**:
```python
def validate_custom_checks(outputs_dir, custom_checks):
    results = {}

    for check in custom_checks:
        if check["type"] == "file_count":
            # Count files matching pattern
            files = glob.glob(f"{outputs_dir}/{check['path']}")
            count = len(files)
            passed = (check["min"] <= count <= check["max"])
            results[check["name"]] = {
                "passed": passed,
                "count": count,
                "expected": f"{check['min']}-{check['max']}"
            }

        elif check["type"] == "content_check":
            # Check keyword occurrences
            file_path = f"{outputs_dir}/{check['file']}"
            with open(file_path) as f:
                content = f.read()
            occurrences = content.count(check["keyword"])
            passed = (occurrences >= check["min_occurrences"])
            results[check["name"]] = {
                "passed": passed,
                "occurrences": occurrences,
                "expected": f">={check['min_occurrences']}"
            }

        elif check["type"] == "script":
            # Run custom validation script
            result = subprocess.run(
                check["command"],
                shell=True,
                cwd=outputs_dir,
                capture_output=True
            )
            passed = (result.returncode == check["expected_exit_code"])
            results[check["name"]] = {
                "passed": passed,
                "exit_code": result.returncode,
                "expected_exit_code": check["expected_exit_code"],
                "stdout": result.stdout.decode(),
                "stderr": result.stderr.decode()
            }

    # All checks must pass
    all_passed = all([r["passed"] for r in results.values()])
    return all_passed, results
```

---

## Success Criteria Report

### Output Format

```json
{
  "agent_name": "code-generator",
  "success_evaluation_timestamp": "2025-10-30T14:42:35Z",
  "overall_success": true,
  "criteria_results": [
    {
      "criterion": "exit_code",
      "passed": true,
      "details": "Exit code 0 (success)"
    },
    {
      "criterion": "required_outputs",
      "passed": true,
      "details": "All required outputs present"
    },
    {
      "criterion": "tests_pass",
      "passed": true,
      "details": "All 42 tests passed"
    },
    {
      "criterion": "no_lint_errors",
      "passed": true,
      "details": "No errors found by pylint"
    },
    {
      "criterion": "coverage",
      "passed": true,
      "details": "Coverage 85% (threshold 80%)",
      "actual_value": 85,
      "threshold": 80
    },
    {
      "criterion": "syntax_valid",
      "passed": true,
      "details": "All code files syntactically valid"
    }
  ],
  "failures": [],
  "warnings": [
    {
      "criterion": "test_execution_time",
      "message": "Tests took 45 seconds (longer than expected 30 seconds)"
    }
  ]
}
```

---

## Integration

### Called from Terminal Orchestrator

```python
from terminal_orchestrator.verification import success_criteria

# After output validation passes
try:
    success_report = success_criteria.evaluate(
        agent_name="code-generator",
        outputs_dir="/tmp/orchestration/outputs/code-generator",
        execution_request=execution_request
    )

    if success_report["overall_success"]:
        print("✓ Success criteria met, agent execution successful")
    else:
        print(f"✗ Success criteria not met: {success_report['failures']}")
        # Mark agent as failed even if outputs are valid

except Exception as e:
    print(f"✗ Success criteria evaluation error: {e}")
```

---

## Summary

**Success Criteria**:
- **Universal**: Exit code 0, required outputs present, no critical errors
- **Agent-Specific**: code-generator (tests pass, no lint errors, coverage), code-reviewer (review complete, no critical issues), data-profiler (profile complete, issues classified), ml-trainer (model trained, metrics recorded, reproducible), react-architect (components created, accessibility passed, tests pass)
- **Custom**: File counts, content checks, script execution

**Gate**: Agent must pass **all** success criteria to be marked as successful

**Integration**: Called after output validation, before merge

**Output**: Success criteria report with overall status, individual criterion results, failures, warnings
