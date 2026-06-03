#context manager controls what each agent sees helps to implement "context boundary"

#regarding the AGENTS.md file that each agent read from, if the planner, implementer etc all read from the same file wont there be context
#corruption, if the architecture were to expand? 
#would it be better if there is a specialised AGENTS.md file for each agent for a more contextualised instruction albeit some of it may be repeated

from pathlib import Path

from harness.contracts import ContextCapsule, PlanContract, TaskContract, ValidationResult

WORKSPACE_ROOT = Path("workspace")

class ContextManager:
    def _read_text(self, relative_path: str) -> str: 
        path = WORKSPACE_ROOT / relative_path
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")
    
    def _read_required_files(self, task_contract: TaskContract) -> dict[str, str]:
        files = {}
        for relative_path in task_contract.required_files:
            files[relative_path] = self._read_text(relative_path)
        return files
    
    def build_for_planner(self, task_contract: TaskContract) -> ContextCapsule: 
        return ContextCapsule(
            agent_name="planner",
            task_contract=task_contract,
            instructions=self._read_text("AGENTS.md"),
            relevant_files=self._read_required_files(task_contract),
            relevant_state={
                "progress": self._read_text("progress.md"),
                "task_breadown": self._read_text("task_breakdown.md"),
            },
            constraints=[
                "Produce a plan only.",
                "Do not generate code.",
                "Only plan changes for allowed files."
            ],
            output_format="PlanContract",
        )
    
    def build_for_implementer(
            self,
            task_contract: TaskContract,
            plan: PlanContract,
    ) -> ContextCapsule:
        return ContextCapsule(
            agent_name="implementer",
            task_contract=task_contract,
            instructions=self._read_text("AGENTS.md"),
            relevant_files=self._read_required_files(task_contract),
            relevant_state={
                "plan": plan,
            },
            constraints=[
                "Generate complete file contents.",
                "Only modify allowed files.",
                "Do not modify state files.",
            ],
            output_format="CodeChangeContract",
        )
    
    def build_for_repairer(
        self,
        task_contract: TaskContract,
        validation_result: ValidationResult,
    ) -> ContextCapsule:
        return ContextCapsule(
            agent_name="repairer",
            task_contract=task_contract,
            instructions=self._read_text("AGENTS.md"),
            relevant_files=self._read_required_files(task_contract),
            relevant_state={
                "validation_result": validation_result,
            },
            constraints=[
                "Repair only validation errors.",
                "Only modify allowed files.",
                "Do not introduce unrelated changes.",
            ],
            output_format="CodeChangeContract",
        )
    
    def build_for_reviewer(self, task_contract: TaskContract) -> ContextCapsule:
        return ContextCapsule(
            agent_name="reviewer",
            task_contract=task_contract,
            instructions=self._read_text("AGENTS.md"),
            relevant_files=self._read_required_files(task_contract),
            relevant_state={},
            constraints=[
                "Review only the completed task.",
                "Do not modify files",
                "Check whether the implementation matches the task contract.",
                "Do not claim success unless validation passed."
            ],
            output_format="ReviewResult",
        )