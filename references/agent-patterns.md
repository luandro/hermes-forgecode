# Multi-Agent Orchestration Patterns with Forge

## Overview

Forge ships three built-in agents with complementary roles, enabling multi-agent workflows without external tooling:

| Agent | Role | Writes code? | Use when |
|-------|------|--------------|----------|
| `sage` | Researcher | No | Understanding architecture, tracing data flow, auditing |
| `muse` | Planner | plans/ only | Designing solutions before touching source code |
| `forge` | Implementer | Yes | Building, fixing, refactoring, testing |

---

## Pattern 1: sage → muse → forge (Research-Plan-Implement)

The safest pattern for significant changes. Each phase validates before proceeding.

```python
import subprocess

repo = "/path/to/repo"

# Phase 1: Research (read-only, no risk)
print("=== Phase 1: Research ===")
research = subprocess.run(
    ['forge', '--agent', 'sage', '-p',
     'How does the current authentication system work? '
     'What are the main components, data flows, and pain points?'],
    cwd=repo, capture_output=True, text=True
)
print(research.stdout)

# Phase 2: Plan (writes plans/plan.md)
print("=== Phase 2: Plan ===")
plan = subprocess.run(
    ['forge', '--agent', 'muse', '-p',
     'Based on the auth system analysis, design a plan to add OAuth2 support. '
     'Consider backward compatibility and migration path.'],
    cwd=repo, capture_output=True, text=True
)
print(plan.stdout)

# Review plans/plan.md before proceeding (optional human checkpoint)
with open(f"{repo}/plans/plan.md") as f:
    print("=== Plan to execute ===")
    print(f.read())

# Phase 3: Implement
print("=== Phase 3: Implement ===")
result = subprocess.run(
    ['forge', '-p', 'Execute the plan in plans/plan.md step by step. '
     'Run tests after each major change.'],
    cwd=repo, capture_output=True, text=True
)
print(result.stdout)
```

---

## Pattern 2: Parallel Workers (Independent Tasks)

Use git worktrees to run multiple forge agents in parallel on independent branches.

```python
import subprocess
import os

repo = "/path/to/repo"

tasks = [
    ("feat/auth-oauth", "Implement OAuth2 authentication using the passport.js library"),
    ("feat/api-pagination", "Add cursor-based pagination to all list endpoints"),
    ("fix/memory-leak", "Fix the memory leak in the WebSocket connection handler"),
]

worktrees = []

# Create worktrees
for branch, _ in tasks:
    wt_path = f"/tmp/forge-{branch.replace('/', '-')}"
    subprocess.run(['git', 'worktree', 'add', wt_path, '-b', branch], cwd=repo)
    worktrees.append(wt_path)

# WARNING: Parallel forge agents share the same API key and rate limit.
# With >2 workers, expect 429 retries — tune with FORGE_RETRY_MAX_ATTEMPTS.
# Always log stderr (stderr=subprocess.STDOUT) — lost stderr hides failures.
# Use timeout= on wait() to prevent zombie worktrees if a task hangs.

# Launch parallel forge agents
processes = []
for (branch, prompt), wt_path in zip(tasks, worktrees):
    p = subprocess.Popen(
        ['forge', '-p', prompt],
        cwd=wt_path,
        stdout=open(f"/tmp/forge-log-{branch.replace('/', '-')}.txt", 'w'),
        stderr=subprocess.STDOUT
    )
    processes.append((branch, p, wt_path))
    print(f"Started: {branch}")

# Wait for all to complete (with timeout to avoid hanging indefinitely)
for branch, p, wt_path in processes:
    try:
        returncode = p.wait(timeout=1800)  # 30 min max per task
        print(f"Completed: {branch} (exit={returncode})")
    except subprocess.TimeoutExpired:
        p.kill()
        print(f"Timed out: {branch} — manual review needed")

# Review and clean up
for _, _, wt_path in processes:
    subprocess.run(['git', 'worktree', 'remove', wt_path, '--force'])
```

---

## Pattern 3: Orchestrator-Workers (Dynamic Task Decomposition)

Use sage to decompose a complex task, then dispatch parallel forge workers.

```python
import subprocess
import json
import os

repo = "/path/to/repo"

# IMPORTANT: Do not parse forge's stdout for structured data.
# Forge one-shot output mixes reasoning traces, ANSI codes, and chat text —
# stdout parsing is brittle and breaks across versions.
# Instead: instruct forge to write structured output to a file, then read that file.

os.makedirs(f"{repo}/plans", exist_ok=True)

# Orchestrator: decompose task into subtasks — write output to a file
subprocess.run(
    ['forge', '--agent', 'sage', '-p',
     'Analyze the codebase and decompose this task into 3-5 independent subtasks: '
     '"Migrate from REST to GraphQL". '
     'Write your result as JSON to plans/subtasks.json with format: '
     '{"subtasks": [{"id": "...", "description": "...", "files": [...]}]}'],
    cwd=repo
)

# Read structured output from file — reliable, no stdout parsing needed
with open(f"{repo}/plans/subtasks.json") as f:
    subtasks_data = json.load(f)
subtasks = subtasks_data['subtasks']

# WARNING: Parallel forge agents share the same API key and rate limit.
# With >2 workers, expect 429 retries — tune with FORGE_RETRY_MAX_ATTEMPTS.

# Dispatch workers in parallel
processes = []
for task in subtasks:
    wt_path = f"/tmp/forge-{task['id']}"
    subprocess.run(['git', 'worktree', 'add', wt_path, '-b', f"graphql/{task['id']}"], cwd=repo)
    
    p = subprocess.Popen(
        ['forge', '-p', task['description']],
        cwd=wt_path,
        stdout=open(f"/tmp/forge-log-{task['id']}.txt", 'w'),
        stderr=subprocess.STDOUT
    )
    processes.append((task['id'], p, wt_path))

# Collect results
for task_id, p, wt_path in processes:
    try:
        p.wait(timeout=1800)
    except subprocess.TimeoutExpired:
        p.kill()
        print(f"Timed out: {task_id}")
        continue
    with open(f"/tmp/forge-log-{task_id}.txt") as f:
        print(f"=== {task_id} ===")
        print(f.read()[-2000:])  # Last 2000 chars

# Clean up
for _, _, wt_path in processes:
    subprocess.run(['git', 'worktree', 'remove', wt_path, '--force'])
```

---

## Pattern 4: Validation Loop (Iterative Improvement)

Use forge to implement, then sage to validate, repeating until criteria are met.

```python
import subprocess
import json

repo = "/path/to/repo"
max_iterations = 3

for i in range(max_iterations):
    print(f"=== Iteration {i+1} ===")
    
    # Implement / fix
    impl = subprocess.run(
        ['forge', '-p', 'Fix all failing tests. Run pytest and fix any failures.'],
        cwd=repo, capture_output=True, text=True
    )
    
    # Validate with sage (read-only — cannot accidentally modify source files)
    subprocess.run(
        ['forge', '--agent', 'sage', '-p',
         'Run the test suite and report results. Do not modify any source files. '
         'Write results to plans/validation.json: '
         '{"passed": N, "failed": N, "issues": [...], "done": true/false}'],
        cwd=repo
    )

    with open(f"{repo}/plans/validation.json") as f:
        report = json.load(f)
    if report.get("done"):
        print("All tests passing. Done.")
        break
    
    print(f"Still failing, iterating...")
else:
    print("Max iterations reached. Manual review needed.")
```

---

## Pattern 5: Staged Review Pipeline

Use sage for security/quality audit before merge.

```python
import subprocess

repo = "/path/to/repo"

checks = [
    ("security", "Audit the staged changes for security vulnerabilities. "
                 "Check for: injection risks, auth bypasses, sensitive data exposure, "
                 "insecure dependencies. Rate severity: critical/high/medium/low."),
    ("performance", "Review staged changes for performance issues: "
                    "N+1 queries, missing indexes, blocking I/O, memory leaks, unnecessary computation."),
    ("correctness", "Review staged changes for logical errors, missing edge cases, "
                    "incorrect error handling, and race conditions."),
]

results = {}
for check_name, prompt in checks:
    result = subprocess.run(
        ['forge', '--agent', 'sage', '-p', prompt],
        cwd=repo, capture_output=True, text=True
    )
    results[check_name] = result.stdout

# Summarize
summary = subprocess.run(
    ['forge', '--agent', 'sage', '-p',
     f'Summarize these code review findings and give a go/no-go recommendation:\n\n'
     f'Security: {results["security"][:500]}\n\n'
     f'Performance: {results["performance"][:500]}\n\n'
     f'Correctness: {results["correctness"][:500]}'],
    cwd=repo, capture_output=True, text=True
)
print(summary.stdout)
```

---

## Choosing a Pattern

| Scenario | Pattern |
|----------|---------|
| Significant feature with unknown scope | sage → muse → forge |
| Multiple unrelated tasks that can run in parallel | Parallel Workers |
| Large refactor needing decomposition | Orchestrator-Workers |
| Flaky tests or iterative quality improvement | Validation Loop |
| Pre-merge review | Staged Review Pipeline |
| Quick one-off task | Direct `forge -p "..."` |

---

## Coordination Tips

- **Pass context between agents** by reading plan files or capturing stdout and passing as context in the next prompt.
- **Use `--conversation-id`** to maintain state across multiple forge invocations for the same logical task.
- **Limit scope per agent** — smaller, well-defined prompts produce better results than broad open-ended ones.
- **Set stopping conditions** in your orchestration loop (`max_iterations`, timeout, explicit "done" signal in output).
- **Use `--sandbox`** for risky experiments so cleanup is just deleting the worktree + branch.
