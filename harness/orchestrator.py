from dataclasses import dataclass

from harness.agents.Implementer import ImplementationAgent
from harness.agents.planner import PlanningAgent
from harness.agents.repairer import RepairAgent
from harness.agents.task_resolver import TaskResolverAgent
from harness.agents.reviewer import ReviewerAgent
from harness.context.context_manager import ContextManager
from harness.state.state_manager import StateManager
from harness.tools.execution_manager import ExecutionManager
from harness.validation.validator import Validator
from harness.completion_gate import CompletionGate
from harness.repair.deterministic_repairs import DeterministicRepairEngine

@dataclass
class HarnessRunResult:
    success: bool
    final_message: str

MAX_LLM_REPAIR_ATTEMPTS = 2

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
        self.reviewer = ReviewerAgent()
        self.completion_gate = CompletionGate()
        self.deterministic_repair_engine = DeterministicRepairEngine()

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
            deterministic_repair = self.deterministic_repair_engine.try_repair(
                task_contract=task_contract,
                validation_result=validation_result,
            )
            
            if deterministic_repair.repaired:
                validation_result = self.validator.validate(task_contract)

        if not validation_result.passed and validation_result.repairable:
            for attempt in range(MAX_LLM_REPAIR_ATTEMPTS):
                if validation_result.passed or not validation_result.repairable:
                    break

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

        review_context = self.context_manager.build_for_reviewer(task_contract)
        review_result = self.reviewer.run(
            context=review_context,
            validation_result=validation_result,
        )

        completion_certificate = self.completion_gate.evaluate(
            task_contract=task_contract,
            validation_result=validation_result,
            review_result=review_result.output,
        )

        self.state_manager.record_run(task_contract, validation_result)

        if completion_certificate.passed:
            return HarnessRunResult(
                success=True,
                final_message=(
                    "Task completed successfully.\n"
                    f"Task: {task_contract.resolved_task}\n"
                    f"Validation profile: {validation_result.profile}"
                    f"Review: {review_result.output.summary}"
                ),
            )
        
        return HarnessRunResult(
            success=False,
            final_message=(
                "Task did not pass completion review.\n"
                f"Task: {task_contract.resolved_task}\n"
                f"Validation passed: {validation_result.passed}\n"
                f"Review issues: {review_result.output.issues}"            
            ),
        )