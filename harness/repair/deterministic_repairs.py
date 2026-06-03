import subprocess
from pathlib import Path

from harness.contracts import TaskContract, ValidationResult


WORKSPACE_ROOT = Path("workspace")


class DeterministicRepairResult:
    def __init__(self, repaired: bool, evidence: list[str]) -> None:
        self.repaired = repaired
        self.evidence = evidence


class DeterministicRepairEngine:
    def try_repair(
        self,
        task_contract: TaskContract,
        validation_result: ValidationResult,
    ) -> DeterministicRepairResult:
        if validation_result.failure_type == "ruff":
            return self._repair_ruff(task_contract)

        return DeterministicRepairResult(
            repaired=False,
            evidence=["No deterministic repair rule matched."],
        )

    def _repair_ruff(self, task_contract: TaskContract) -> DeterministicRepairResult:
        files = [
            path
            for path in task_contract.allowed_files
            if path.endswith(".py")
        ]

        if not files:
            return DeterministicRepairResult(
                repaired=False,
                evidence=["No Python files available for Ruff repair."],
            )

        result = subprocess.run(
            ["ruff", "check", *files, "--fix"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        return DeterministicRepairResult(
            repaired=result.returncode in [0, 1],
            evidence=[
                "Ran deterministic Ruff repair.",
                result.stdout + result.stderr,
            ],
        )
