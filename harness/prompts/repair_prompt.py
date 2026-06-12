from harness.contracts import ContextCapsule

def build_repair_instructions() -> str:
    return """
You are the Repair Agent inside a harness-controlled coding system.

You are not the orchestrator.
You are not the validator. 
You are not the state manager.

Your job: 
- Repair only the validation failure provided.
- Modify only files listed in allowed_files.
- Return complete file contents for every file you modify.
- Do not rewrite unrelated code.
- Do not edit state files.
- Do not claim validation success.

Required output format: 

FILE: relative/path.py
```python
full file content
```

Hard rules: 
- Use only relative paths.
- Do not prefic paths with workspace/.
- Only output files listed in allowed_files.
- Include complete file contents, not diffs.
- Do not include explanation before or after FILE blocks.
"""

def build_repair_prompt(context: ContextCapsule) -> str:
    task = context.task_contract
    validation_result = context.relevant_state.get("validation_result")

    files_section=[]

    for path, content in context.relevant_files.items():
        files_section.append(
            f"""
            =====FILE:{path}=====
            {content}
            =====END FILE:{path}=====
            """
        )

    files_text = "\n".join(files_section)

    return f"""
WORKSPACE INSTRUCTION

{context.instructions}
    
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

VALIDATION FAILURE

failure_type:
{validation_result.failure_type if validation_result else "unknown"}

command_outputs:
{validation_result.command_outputs if validation_result else []}

CURRENT FILES

{files_text}

CONSTRAINTS

{context.constraints}

Repair the validation failure using only the required FILE block format.
"""