# Add Structured Logging (Python Backend)

## Role

You are a senior backend engineer.

---

## Objective

Add structured, production-quality logging to the provided code.

---

## Requirements

- Use `from app.core.logger import get_logger`
- Use `logger = get_logger(__name__)`
- Add logs at appropriate levels:
  - DEBUG → internal state, variables
  - INFO → key actions, successful operations
  - WARNING → recoverable issues
  - ERROR → failures and exceptions

- DO NOT:
  - duplicate logs
  - log sensitive data
  - over-log trivial lines

---

## Logging Guidelines

- Log at function entry (only when meaningful)
- Log important variables (inputs, counts, results)
- Log before and after external calls (APIs, DB, file I/O)
- Log exceptions with context
- Keep messages concise and structured

## Output

Output the full file with it's current contents plus the logs as 1 file.
