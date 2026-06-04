from dataclasses import dataclass

from harness.contracts import ReviewResult, TaskContract, ValidationResult

@dataclass
class CompletionCertificate: 
    passed: bool
    evidence: list[str]
    reason: str | None=None

class CompletionGate:
    def evaluate(
        self,
        task_contract: TaskContract,
        validation_result: ValidationResult,
        review_result: ReviewResult,
    ) -> CompletionCertificate:
        evidence = []

        if not validation_result.passed:
            return CompletionCertificate(
                passed=False,
                evidence=validation_result.command_outputs,
                reason="Validation failed.",
            )
        
        evidence.append("Validation passed.")

        if not review_result.passed:
            return CompletionCertificate(
                passed=False,
                evidence=review_result.issues,
                reason="Review failed",
            )
        
        evidence.append("Review passed.")

        return CompletionCertificate(
            passed=True,
            evidence=evidence,
        )