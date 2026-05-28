import json
from datetime import datetime
from pathlib import Path

from harness.contracts import TaskContract, ValidationResult

WORKSPACE_ROOT = Path("workspace")

class StateManager:
    def record_run(
        self,
        task_contract: TaskContract,
        validation_result: ValidationResult,
    ) -> None:
        if validation_result.passed:
            self._append_progress(task_contract)
            self._append_run_history(task_contract,validation_result)
        else: 
            self._append_failure_log(task_contract, validation_result)
            self._append_run_history(task_contract, validation_result)

    def _append_progress(self, task_contract: TaskContract) -> None:
        path = WORKSPACE_ROOT / "progress.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else "# Pregress\n"

        entry = (
            f"\n## {datetime.now().isoformat(timespec='seconds')}\n"
            f"- Completed: {task_contract.resolved_task}\n"
            f"- Validation profile: {task_contract.validation_profile}\n"
        )

        path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")

    def _append_run_history(
        self,
        task_contract: TaskContract,
        validation_result: ValidationResult,
    ) -> None:
        path = WORKSPACE_ROOT / "run_history.json"
        history = self._read_json_list(path)

        history.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "task_id": task_contract.task_id,
                "resolved_task": task_contract.resolved_task,
                "passed": validation_result.passed,
                "profile": validation_result.profile,
                "failure_type": validation_result.failure_type,
            }
        )

        path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def _append_failure_log(
        self,
        task_contract: TaskContract,
        validation_result: ValidationResult,
    ) -> None:
        path = WORKSPACE_ROOT / "failure_log.json"
        failures = self._read_json_list(path)

        failures.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "task_id": task_contract.task_id,
                "resolved_task": task_contract.resolved_task,
                "failure_type": validation_result.failure_type,
                "outputs": validation_result.command_outputs,
            }
        )

        path.write_text(json.dumps(failures, indent=2), encoding="utf-8")

    def _read_json_list(self, path: Path) -> list:
        if not path.exists():
            return []

        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return []

        return json.loads(text)