from harness.contracts import AgentResult, CodeChangeContract, ContextCapsule
from harness.repair.deterministic_repairs import DeterministicRepairEngine

class RepairAgent:
    name = "repairer"

    def __init__(self) -> None:
        self.deterministic_repairs = DeterministicRepairEngine()

    def run(self, context: ContextCapsule) -> AgentResult:
        validation_result = context.relevant_state["validation_result"]
        repair_result = self.deterministic_repairs.try_repair(
            task_contract=context.task_contract,
            validation_result=validation_result,
        )

        if repair_result.repaired:
            return AgentResult(
                agent_name=self.name,
                status="pass",
                output=CodeChangeContract(
                    changes=[],
                    notes="Deterministic repair was applied directly to workspace files.",
                ),
                evidence=repair_result.evidence,
            )

        return AgentResult(
            agent_name=self.name,
            status="fail",
            output=CodeChangeContract(
                changes=[],
                notes="No deterministic repair was applied.",
            ),
            evidence=[
                f"Validation failed with type: {validation_result.failure_type}",
                *repair_result.evidence,
            ],
        )
