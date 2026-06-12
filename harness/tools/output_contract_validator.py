from harness.contracts import CodeChangeContract, TaskContract

def validate_code_change_contract(
    task_contract: TaskContract,
    code_change_contract: CodeChangeContract,
    require_all_required_files: bool = False,
) -> None:
    allowed = {path.replace("\\", "/") for path in task_contract.allowed_files}
    required = {path.replace("\\","/") for path in task_contract.required_files}
    returned = {
        change.path.replace("\\", "/")
        for change in code_change_contract.changes
    }

    unexpected = returned - allowed

    if unexpected:
        raise ValueError(
            f"Output contains files outside allowed scope: {sorted(unexpected)}"
        )
    
    if require_all_required_files:
        missing = required - returned

        if missing:
            raise ValueError(
                f"Output is missing required files: {sorted(missing)}"
            )
    
    