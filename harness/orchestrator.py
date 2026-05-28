from dataclasses import dataclass

from harness.agents.Implementer import ImplementationAgent
from harness.agents.planner import PlanningAgent
from harness.agents.repairer import RepairAgent
from harness.agents.task_resolver import TaskResolverAgent
from harness.context.context_manager import ContextManager
from harness.state.state_manager import StateManager
from harness.tools.execution_manager import ExecutionManager
from harness.validation.validator import Validator

@dataclass
class HarnessRunResult:
    success: bool
    final_message: str

class Orchestrator:
    def __init__(self) -> None:
        self.task_resolver = TaskResolverAgent()
        self.context_manager = ContextManager()
        self.planner = PlanningAgent()
        self.implementer = ImplementationAgent()
        self.execution_manager = ExecutionManager()
        self.validator = Validator()
        self.repairer = RepairAgent()
        self.state_manager = StateManager()

    def run(self, user_request: str) -> HarnessRunResult:
        task_contract = self.task_resolver.resolve(user_request)

        planner_context = self.context_manager.build_for_planner(task_contract)
        plan_result = self.planner.run(planner_context)

        if plan_result.status != "pass":
            return HarnessRunResult(
                success=False,
                final_message="Implementation failed",
            )
        
        implementer_context = self.context_manager.build_for_implementer(
            task_contract=task_contract,
            plan=plan_result.output,
        )

        implementation_result = self.implementer.run(implementer_context)

        if implementation_result.status != "pass":
            return HarnessRunResult(
                success=False,
                final_message="Implementation failed.",
            )

        self.execution_manager.apply_changes(
            task_contract=task_contract,
            code_change_contract=implementation_result.output
        )

        validation_result = self.validator.validate(task_contract)

        if not validation_result.passed and validation_result.repairable:
            repair_context = self.context_manager.build_for_repairer(
                task_contract=task_contract,
                validation_result=validation_result,
            )
            repair_result = self.repairer.run(repair_context)

            if repair_result.status == "pass":
                self.execution_manager.apply_changes(
                    task_contract=task_contract,
                    code_change_contract=repair_result.output,
                )
                validation_result = self.validator.validate(task_contract)
        self.state_manager.record_run(task_contract, validation_result)

        if validation_result.passed:
            return HarnessRunResult(
                success=True,
                final_message=(
                    "Task completed successfully.\n"
                    f"Task: {task_contract.resolved_task}\n"
                    f"Validation profile: {validation_result.profile}"
                ),
            )
        
        return HarnessRunResult(
            success=False,
            final_message=(
                "Task failed validation.\n"
                f"Task: {task_contract.resolved_task}\n"
                f"Failure type: {validation_result.failure_type}\n"
                f"Output:\n{validation_result.command_outputs[-1] if validation_result.command_outputs else ''}"
            ),
        )