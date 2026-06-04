from harness.contracts import AgentResult, ContextCapsule, ReviewResult, ValidationResult

class ReviewerAgent:
    name = "reviewer"

    def run(
        self,
        context: ContextCapsule,
        validation_result: ValidationResult,
    ) -> AgentResult:
        task = context.task_contract
        files = context.relevant_files

        issues: list[str] = []
        evidence: list[str] = []

        calculator_code = files.get("src/calculator.py", "")
        test_code = files.get("tests/test_calculator.py", "")

        if not validation_result.passed:
            issues.append("Validation did not pass.")
        else:
            evidence.append("Validation passed.")

        task_text = task.resolved_task.lower()

        if "add" in task_text or "addition" in task_text:
            if "def add" not in calculator_code:
                issues.append("Expected add function was not found in calculator.py.")
            if "test_add" not in test_code:
                issues.append("Expected add test was not found.")

        if "subtract" in task_text:
            if "def subtract" not in calculator_code:
                issues.append("Expected subtract function was not found in calculator.py.")
            if "test_subtract" not in test_code:
                issues.append("Expected subtract test was not found.")

        if "multiply" in task_text or "multiplication" in task_text:
            if "def multiply" not in calculator_code:
                issues.append("Expected multiply function was not found in calculator.py.")
            if "test_multiply" not in test_code:
                issues.append("Expected multiply test was not found.")

        if "divide" in task_text or "division" in task_text:
            if "def divide" not in calculator_code:
                issues.append("Expected divide function was not found in calculator.py.")
            if "test_divide" not in test_code:
                issues.append("Expected divide test was not found.")
            if "raise" not in calculator_code and "ZeroDivisionError" not in calculator_code:
                issues.append("Division implementation may not handle divide-by-zero explicitly.")

        passed = len(issues) == 0

        review = ReviewResult(
            passed=passed,
            summary="Review passed." if passed else "Review found issues.",
            issues=issues,
            evidence=evidence,
        )

        return AgentResult(
            agent_name=self.name,
            status="pass" if passed else "fail",
            output=review,
            evidence=evidence,
        )