from pathlib import Path

from harness.contracts import CodeChangeContract, TaskContract

WORKSPACE_ROOT = Path("workspace")

class ExecutionManager:
    def apply_changes(
        self,
        task_contract: TaskContract,
        code_change_contract: CodeChangeContract,
    ) -> None:
        allowed = set(task_contract.allowed_files)
        forbidden = set(task_contract.forbidden_files)

        for change in code_change_contract.changes:
            normalized_path = change.path.replace("\\", "/")

            if normalized_path.startswith("workspace/"):
                raise ValueError(f"Invalid path includes workspace prefix: {change.path}")
            
            if normalized_path in forbidden:
                raise ValueError(f"Attempted to modify forbidden file: {change.path}")
            
            if normalized_path not in allowed:
                raise ValueError("f:Attempted to modify file outside allowed scope: {change.path}")
            
            target_path = WORKSPACE_ROOT / normalized_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(change.content, encoding="utf-8")