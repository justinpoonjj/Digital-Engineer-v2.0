from harness.contracts import AgentResult, CodeChangeContract, ContextCapsule
from harness.prompts.repair_prompt import (
    build_repair_instructions,
    build_repair_prompt,
)
from harness.tools.file_block_parser import FileBlockParseError, parse_file_blocks
from harness.tools.output_contract_validator import validate_code_change_contract


class RepairAgent:
    name = "repairer"

    def __init__(self, llm=None) -> None:
        if llm is None:
            from harness.models.llm_service import LLMService

            llm = LLMService()

        self.llm = llm

    def run(self, context: ContextCapsule) -> AgentResult:
        instructions = build_repair_instructions()
        prompt = build_repair_prompt(context)

        try:
            raw_output = self.llm.generate(
                instructions=instructions,
                prompt=prompt,
            )

            code_change_contract = parse_file_blocks(raw_output)
            validate_code_change_contract(context.task_contract,code_change_contract)

            return AgentResult(
                agent_name=self.name,
                status="pass",
                output=code_change_contract,
                evidence=[
                    "LLM generated repair FILE block output. ",
                    "Harness paresed repair output into CodeChangeContract. "
                ]
            )
        except FileBlockParseError as error:
            return AgentResult(
                agent_name=self.name,
                status="fail",
                output=CodeChangeContract(
                    changes=[],
                    notes=f"Could not parse LLM repair output: {error}",
                ),
                evidence=[
                    "LLM repair output failed FILE block parsing."
                ],
            )
        
        except Exception as error:
            return AgentResult(
                agent_name=self.name,
                status="fail",
                output=CodeChangeContract(
                    changes=[],
                    notes=f"LLM repair failed: {error}",
                ),
                evidence=[
                    "LLM repair service call failed.",
                ],
            )
