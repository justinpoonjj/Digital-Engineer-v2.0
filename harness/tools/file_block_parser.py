import re

from harness.contracts import CodeChange, CodeChangeContract

FILE_BLOCK_PATTERN = re.compile(
    r"FILE:\s*(?P<path>[^\n]+)\n```(?:python)?\n(?P<content>.*?)\n```",
    re.DOTALL,
)

class FileBlockParseError(ValueError):
    pass

def parse_file_blocks(raw_output: str) -> CodeChangeContract:
    matches = list(FILE_BLOCK_PATTERN.finditer(raw_output))

    if not matches: 
        raise FileBlockParseError("No valid FILE blocks found in LLM output")
    
    changes: list[CodeChange] = []

    for match in matches: 
        path = match.group("path").strip()
        content = match.group("content")

        if not path:
            raise FileBlockParseError("FILE block is missing a path")
        
        changes.append(
            CodeChange(
                path=path,
                content=content.rstrip() + "\n",
                reason="LLM-generated implementation",
            )
        )

    return CodeChangeContract(
        changes=changes,
        notes="Parsed from LLM FILE block output.",
    )