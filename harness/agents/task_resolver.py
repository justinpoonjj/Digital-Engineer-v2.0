from harness.contracts import TaskContract

#This is intentionally deterministic for now. Later, you can use an LLM for task resolution.

class TaskResolverAgent: 
    name = "task_resolver"

    def resolve(self, user_request: str) -> TaskContract:
        normalized = user_request.lower()

        if "subtract" in normalized:
            task_id = "calculator-subtract"
            resolved_task = "Add a subtract(a, b) function to the calculator and test it."
        elif "multiply" in normalized or "multiplication" in normalized:
            task_id = "calculator-multiply"
            resolved_task = "Add a multiply(a, b) function to the calculator and test it."
        elif "divide" in normalized or "division" in normalized:
            task_id = "calculator-divide"
            resolved_task = "Add a divide(a, b) function to the calculator and test it."
        else: 
            task_id = "calculator-generic"
            resolved_task = user_request

        return TaskContract(
            task_id=task_id,
            user_request=user_request,
            resolved_task=resolved_task,
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
                "feature_list.json",
                "run_history.json",
                "failure_log.json",
                "task_breakdown.md",
            ],
            validation_profile="calculator",
            completion_evidence=[
                "pytest tests/test_calculator.py passes",
                "ruff check src/calculator.py tests/test_calculator.py passes",
            ],
        )