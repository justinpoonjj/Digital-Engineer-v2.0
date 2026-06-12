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
class StageTrace: 
    stage: str
    status: str
    input_summary: str
    output_summary: str
    evidence: list[str]

@dataclass
class HarnessRunResult:
    success: bool
    final_message: str
    trace: list[StageTrace]

MAX_LLM_REPAIR_ATTEMPTS = 4

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
        trace = []
        
        task_contract = self.task_resolver.resolve(user_request)

        planner_context = self.context_manager.build_for_planner(task_contract)
        plan_result = self.planner.run(planner_context)

        trace.append(StageTrace(
            stage="planning",
            status=plan_result.status,
            input_summary=task_contract.resolved_task,
            output_summary=str(plan_result.output),
            evidence=plan_result.evidence,
        ))

        if plan_result.status != "pass":
            return HarnessRunResult(
                success=False,
                final_message="Implementation failed",
                trace=trace,
            )
        
        implementer_context = self.context_manager.build_for_implementer(
            task_contract=task_contract,
            plan=plan_result.output,
        )

        implementation_result = self.implementer.run(implementer_context)

        trace.append(StageTrace(
            stage="implementation",
            status=implementation_result.status,
            input_summary=str(plan_result.output),
            output_summary=str(implementation_result.output),
            evidence=implementation_result.evidence,
        ))

        if implementation_result.status != "pass":
            return HarnessRunResult(
                success=False,
                final_message="Implementation failed.",
                trace=trace,
            )

        self.execution_manager.apply_changes(
            task_contract=task_contract,
            code_change_contract=implementation_result.output
        )

        validation_result = self.validator.validate(task_contract)
        repair_failure_type = validation_result.failure_type

        trace.append(StageTrace(
            stage="validation",
            status="pass" if validation_result.passed else "fail",
            input_summary=task_contract.validation_profile,
            output_summary=f"failure_type={validation_result.failure_type}",
            evidence=validation_result.command_outputs,
        ))

        for attempt in range(MAX_LLM_REPAIR_ATTEMPTS):
            if validation_result.passed or not validation_result.repairable:
                break

            if not validation_result.passed and validation_result.repairable:
                deterministic_repair = self.deterministic_repair_engine.try_repair(
                    task_contract=task_contract,
                    validation_result=validation_result,
                )
                
                if deterministic_repair.repaired:
                    validation_result = self.validator.validate(task_contract)

                trace.append(StageTrace(
                    stage="deterministic_repair",
                    status="pass" if deterministic_repair.repaired else "fail",
                    input_summary=f"failure_type={repair_failure_type}",
                    output_summary="Deterministic repair attempted.",
                    evidence=deterministic_repair.evidence,
                ))

            if not validation_result.passed and validation_result.repairable:
                

                repair_context = self.context_manager.build_for_repairer(
                    task_contract=task_contract,
                    validation_result=validation_result,
                )

                current_failure_type = validation_result.failure_type

                repair_result = self.repairer.run(repair_context)

                if repair_result.status == "pass":
                    self.execution_manager.apply_changes(
                        task_contract=task_contract,
                        code_change_contract=repair_result.output,
                    )

                    validation_result = self.validator.validate(task_contract)

                trace.append(StageTrace(
                    stage=f"llm_repair_attempt_{attempt + 1}",
                    status=repair_result.status,
                    input_summary=f"failure_type={current_failure_type}",
                    output_summary=str(repair_result.output),
                    evidence=repair_result.evidence,
                ))

        review_context = self.context_manager.build_for_reviewer(task_contract)
        review_result = self.reviewer.run(
            context=review_context,
            validation_result=validation_result,
        )

        trace.append(StageTrace(
            stage="review",
            status=review_result.status,
            input_summary=(
                f"task={task_contract.resolved_task}; "
                f"validation_passed={validation_result.passed}; "
                f"failure_type={validation_result.failure_type}"
            ),
            output_summary=str(review_result.output),
            evidence=review_result.evidence,
        ))

        completion_certificate = self.completion_gate.evaluate(
            task_contract=task_contract,
            validation_result=validation_result,
            review_result=review_result.output,
        )

        trace.append(StageTrace(
            stage="completion_gate",
            status="pass" if completion_certificate.passed else "fail",
            input_summary=(
                f"validation_passed={validation_result.passed}; "
                f"review_passed={review_result.output.passed}"
            ),
            output_summary=str(completion_certificate.reason),
            evidence=completion_certificate.evidence,
        ))

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
                trace=trace
            )
        
        return HarnessRunResult(
            success=False,
            final_message=(
                "Task did not pass completion review.\n"
                f"Task: {task_contract.resolved_task}\n"
                f"Validation passed: {validation_result.passed}\n"
                f"Review issues: {review_result.output.issues}"            
            ),
            trace=trace
        )