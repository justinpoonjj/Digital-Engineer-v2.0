from dataclasses import dataclass, field
from typing import Literal 

@dataclass
class TaskContract: 
    task_id: str
    user_request: str
    resolved_task: str
    task_type: str
    requried_files: str
    allowed_files: list[str]
    forbidden_files: list[str]
    validation_profile: str
    completion_evidence: list[str]

@dataclass
class ContextCapsule:
    agent_name: str
    task_contract: TaskContract
    instructions: str
    relevant_files: dict[str, str]
    relevant_state: dict
    constraints: list[str]
    output_format: str

@dataclass
class PlanContract: 
    summary: str
    target_files: list[str]
    steps: list[str]
    risks: list[str]
    validation_plan: list[str]

@dataclass
class CodeChange: 
    path: str
    content: str
    reason: str

@dataclass
class CodeChangeContract: 
    changes: list[CodeChange]
    notes: str = ""

@dataclass
class ValidationResult: 
    passed: bool 
    profile: str
    command_outputs: list[str]
    failure_type: str | None = None
    repairable = bool = False

@dataclass
class AgentResult:
    agent_name = str
    status: Literal["pass", "fail", "needs_repair"]
    output: object
    evidence: list[str] = field(default_factory=list)