from harness.contracts import ContextCapsule

def build_implementer_instructions() -> str:
    return """
You are the Implementation Agent inside a harness-controlled coding system.

You are not the orchestrator.
You are not the validator.
You are not the state manager.

Your job:
- Modify only the files allowed by the task contract.
- Return complete file contents for every file you modify.
- Do not explain outside the required output format.
- Do not edit state files.
- Do not claim validation success.

Required output format:

FILE: relative/path.py
```python
full file content
```

Hard rules:

Use only relative paths.
Do not prefix paths with workspace/.
Only output files listed in allowed_files.
Include complete file contents, not diffs.
Do not include markdown explanation before or after the FILE blocks.
"""

def build_implementer_prompt(context: ContextCapsule) -> str:
    task = context.task_contract

    files_section = []

    for path, content in context.relevant_files.items():
        files_section.append(
            f"""
            ===== FILE: {path} =====
            {content}
            ===== END FILE: {path} =====
            """
        )

    files_text = "\n".join(files_section)

    return f"""
TASK CONTRACT

task_id: 
{task.task_id}

resolved_task: 
{task.resolved_task}

required_files: 
{task.required_files}

allowed_files:
{task.allowed_files}

forbidden_files:
{task.forbidden_files}

validation_profile:
{task.validation_profile}

completion_evidence:
{task.completion_evidence}

PLANNER OUTPUT

{context.relevant_state.get("plan")}

CURRENT FILES

{files_text}

CONTRAINTS

{context.constraints}

Now produce the implemntation using the required FILE block format.
"""