#AGENTS.md

## Project Summary

This workspace is controlled by the Digital Engineer harness.

## Hard Rules

- Work on one implementation task at a time.
- Only edit files allowed by the current task contract.
- Do not modify harness files.
- Do not modify state files directly.
- Generated code must be validated before the task is marked complete.
- If validation fails, repair only the files in scope

## Output Rule

Implementation agents must return complete file contents using: 

FILE: relative/path.py
```python
full file content
```