from harness.contracts import AgentResult, CodeChangeContract, ContextCapsule
from harness.models.llm_service import LLMService
from harness.prompts.implementer_prompt import (
    build_implementer_instructions,
    build_implementer_prompt,
)
from harness.tools.file_block_parser import FileBlockParseError, parse_file_blocks

class ImplementationAgent: 
    name = "implementer"

    def __init__(self) -> None:
        self.llm = LLMService()
    
    def run(self, context: ContextCapsule) -> AgentResult:
        instructions = build_implementer_instructions()
        prompt = build_implementer_prompt(context)

        try: 
            raw_output = self.llm.generate(
                instructions=instructions,
                prompt=prompt,
            )

            code_change_contract = parse_file_blocks(raw_output)
        
            return AgentResult(
            agent_name=self.name,
            status="pass",
            output=code_change_contract,
            evidence=[
                "LLM generated FILE block output.",
                "Harness parsed output into CodeChangeContract.",
            ],
        )

        except FileBlockParseError as error:
            return AgentResult(
                agent_name="self.name",
                status="fail",
                output=CodeChangeContract(
                    changes=[],
                    notes=f"Could not parse LLM output: {error}",
                ),
                evidence=[
                    "LLM output failed FILE block parsing.",
                ],
            )

        except Exception as error:
            return AgentResult(
                agent_name="self.name",
                status="fail",
                output=CodeChangeContract(
                    changes=[],
                    notes=f"LLM implementation failed: {error}",
                ),
                evidence=[
                    "LLM service call failed.",
                ],
            )