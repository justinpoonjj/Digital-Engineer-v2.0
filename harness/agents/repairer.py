from harness.contracts import AgentResult,CodeChangeContract, ContextCapsule

class RepairAgent:
    name = "repairer"

    def run(self, context: ContextCapsule) -> AgentResult:
        validation_result = context.relevant_state["validation_result"]

        return AgentResult(
            agent_name=self.name,
            status="fail",
            output=CodeChangeContract(
                changes=[],
                notes="No deterministic repair rule available yet.",
            ),
            evidence=[
                f"Validation failed with type: {validation_result.failure_type}",
                "Repair agent was invoked but did not apply changes",
            ],
        )
