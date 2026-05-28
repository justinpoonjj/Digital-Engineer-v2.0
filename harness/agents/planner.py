from harness.contracts import AgentResult, ContextCapsule, PlanContract

class PlanningAgent: 
    name = "planner"

    def run(self, context: ContextCapsule) -> AgentResult:
        task = context.task_contract

        plan = PlanContract(
            summary=f"Implement and test: {task.resolved_task}",
            target_files=task.required_files,
            steps=[
                "Inspect the existing calculator source and tests.",
                "Add the requested function to src/calculator.py.",
                "Add or update tests in tests/test_calculator.py.",
                "Run the calculator validation profile.",
            ],
            risks=[
                "Import paths may fail if tests are not run from the workspace root.",
                "The implementation may forget to update tests",       
            ],
            validation_plan=[
                "pytest tests/test_calculator.py",
                "ruff check src/calculator.py tests/test_calculator.py",
            ],
        )

        return AgentResult(
            agent_name=self.name,
            status="pass",
            output=plan,
            evidence=["Plan created from bounded planner context."]
        )