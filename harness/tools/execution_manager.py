from pathlib import Path

from harness.contracts import CodeChangeContract, TaskContract

WORKSPACE_ROOT = Path("workspace")

class ExecutionManager:
    def apply_changes(
        self,
        task_contract: TaskContract,
        code_change_contract: CodeChangeContract,
    ) -> None:
        allowed = {path.replace("\\", "/") for path in task_contract.allowed_files}
        forbidden = {path.replace("\\", "/") for path in task_contract.forbidden_files}

        for change in code_change_contract.changes:
            normalized_path = change.path.replace("\\","/").strip()

            self._validate_path(
                normalized_path=normalized_path,
                allowed=allowed,
                forbidden=forbidden,
            )

            target_path = (WORKSPACE_ROOT / normalized_path).resolve()

            if not str(target_path).startswith(str(WORKSPACE_ROOT)):
                raise ValueError(f"Path escaped workspace: {change.path}")
            
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(change.content, encoding="utf-8")

    def _validate_path(
        self,
        normalized_path: str,
        allowed: set[str],
        forbidden: set[str],
    ) -> None:
        if not normalized_path:
            raise ValueError("Empty file path is not allowed")
        
        if normalized_path.startswith("workspace/"):
            raise ValueError(f"Invalid path includes workspace prefix: {normalized_path}")
        
        if normalized_path.startswith("../") or "/../" in normalized_path:
            raise ValueError(f"Path traversal is not allowed: {normalized_path}")
        
        if normalized_path.startswith("/") or ":" in normalized_path:
            raise ValueError (f"Absolute paths are not allowed: {normalized_path}")
        
        if normalized_path in forbidden: 
            raise ValueError(f"Attempted to modify forbidden file: {normalized_path}")
        
        if normalized_path not in allowed:
            raise ValueError(f"Attempted to modify file outside allowed scope: {normalized_path}")