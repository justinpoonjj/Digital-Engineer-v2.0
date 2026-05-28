import subprocess
from pathlib import Path

from harness.contracts import TaskContract, ValidationResult

WORKSPACE_ROOT = Path("workspace")

class Validator: 
    def validate(self, task_contract: TaskContract) -> ValidationResult:
        missing_file = [
            path for path in task_contract.requried_files
            if not (WORKSPACE_ROOT / path).exists()
        ]

        if missing_file:
            return ValidationResult(
                passed=False,
                profile=task_contract.validation_profile,
                command_outputs=[f"Missing required files: {missing_file}"],
                failure_type="generation",
                repairable=False,
            )
        
        if task_contract.validation_profile == "calculator":
            return self._run_calculator_profile()
        
        return ValidationResult(
            passed=False,
            profile=task_contract.validation_profile,
            command_outputs=["Unknown validation profile."],
            failure_type="validation_profile",
            repariable=False,
        )
    
    def _run_calculator_profile(self) -> ValidationResult:
        outputs = []

        pytest_result = subprocess.run(
            ["pytest", "tests/test_calculator.py"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        outputs.append(pytest_result.stdout + pytest_result.stderr)

        if pytest_result.returncode != 0:
            return ValidationResult(
                passed=False,
                profile="calculator",
                command_outputs=outputs,
                failure_type="pytest",
                repairable=True,
            )

        ruff_result = subprocess.run(
            ["ruff", "check", "src/calculator.py", "tests/test_calculator.py"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        outputs.append(ruff_result.stdout + ruff_result.stderr)

        if ruff_result.returncode != 0:
            return ValidationResult(
                passed=False,
                profile="calculator",
                command_outputs=outputs,
                failure_type="ruff",
                repairable=True,
            )
    
        return ValidationResult(
            passed=True,
            profile="calculator",
            command_outputs=outputs,
        )