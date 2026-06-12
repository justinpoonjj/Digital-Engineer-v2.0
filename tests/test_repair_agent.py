import pytest

from harness.agents.repairer import RepairAgent
from harness.contracts import ContextCapsule, TaskContract, ValidationResult


class FakeRepairLLM:
    def generate(self, instructions: str, prompt: str) -> str:
        return """FILE: src/calculator.py
```python
def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```
"""


class FakeBadRepairLLM:
    def generate(self, instructions: str, prompt: str) -> str:
        return """FILE: random/file.py
```python
print("bad")
```
"""


@pytest.fixture
def repair_context() -> ContextCapsule:
    task_contract = TaskContract(
        task_id="calculator-task",
        user_request="Fix divide",
        resolved_task="Fix divide(a, b) so it divides and raises on zero.",
        task_type="calculator_feature",
        required_files=[
            "src/calculator.py",
            "tests/test_calculator.py",
        ],
        allowed_files=[
            "src/calculator.py",
            "tests/test_calculator.py",
        ],
        forbidden_files=[
            "AGENTS.md",
            "progress.md",
            "run_history.json",
            "failure_log.json",
        ],
        validation_profile="calculator",
        completion_evidence=[],
    )

    validation_result = ValidationResult(
        passed=False,
        profile="calculator",
        command_outputs=[
            "tests/test_calculator.py::test_divide FAILED\nassert 8 == 2"
        ],
        failure_type="pytest",
        repairable=True,
    )

    return ContextCapsule(
        agent_name="repairer",
        task_contract=task_contract,
        instructions="Repair only validation errors.",
        relevant_files={
            "src/calculator.py": """def add(a, b):
    return a + b


def divide(a, b):
    return a * b
""",
            "tests/test_calculator.py": """import pytest

from calculator import add, divide


def test_divide():
    assert divide(4, 2) == 2


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)
""",
        },
        relevant_state={
            "validation_result": validation_result,
        },
        constraints=[
            "Only modify allowed files.",
            "Return complete file contents.",
        ],
        output_format="CodeChangeContract",
    )


def test_repairer_accepts_valid_single_file_repair(
    repair_context: ContextCapsule,
) -> None:
    repairer = RepairAgent(llm=FakeRepairLLM())

    result = repairer.run(repair_context)

    assert result.status == "pass"
    assert result.output.changes
    assert [change.path for change in result.output.changes] == ["src/calculator.py"]
    assert "return a / b" in result.output.changes[0].content


def test_repairer_rejects_random_files(
    repair_context: ContextCapsule,
) -> None:
    repairer = RepairAgent(llm=FakeBadRepairLLM())

    result = repairer.run(repair_context)

    assert result.status == "fail"
    assert "outside allowed scope" in result.output.notes
