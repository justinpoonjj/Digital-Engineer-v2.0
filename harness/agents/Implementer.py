from harness.contracts import AgentResult, CodeChange, CodeChangeContract, ContextCapsule

class ImplementationAgent: 
    name = "implementer"

    def run(self, context: ContextCapsule) -> AgentResult: 
        request = context.task_contract.resolved_task.lower()

        calculator_code = context.relevant_files.get("src/calculator.py", "")
        test_code = context.relevant_files.get("tests/test_calculator.py", "")

        changes: list[CodeChange] = []

        if "subtract" in request:
            if "def subtract" not in calculator_code:
                calculator_code = calculator_code.rstrip() + "\n\n\ndef subtract(a: int, b: int) -> int:\n    return a - b\n"

            if "test_subtract" not in test_code:
                test_code = self._ensure_import(test_code, "subtract")
                test_code = test_code.rstrip() + "\n\n\ndef test_subtract():\n    assert subtract(5, 3) == 2\n"

        elif "multiply" in request:
            if "def multiply" not in calculator_code:
                calculator_code = calculator_code.rstrip() + "\n\n\ndef multiply(a: int, b: int) -> int:\n    return a * b\n"

            if "test_multiply" not in test_code:
                test_code = self._ensure_import(test_code, "multiply")
                test_code = test_code.rstrip() + "\n\n\ndef test_multiply():\n    assert multiply(5, 3) == 15\n"

        elif "divide" in request:
            if "def divide" not in calculator_code:
                calculator_code = calculator_code.rstrip() + "\n\n\ndef divide(a: int, b: int) -> float:\n    if b == 0:\n        raise ValueError('Cannot divide by zero')\n    return a / b\n"

            if "test_divide" not in test_code:
                test_code = self._ensure_import(test_code, "divide")
                test_code = test_code.rstrip() + "\n\n\ndef test_divide():\n    assert divide(6, 3) == 2\n\n\ndef test_divide_by_zero():\n    import pytest\n\n    with pytest.raises(ValueError):\n        divide(6, 0)\n"

        else:
            return AgentResult(
                agent_name=self.name,
                status="fail",
                output=CodeChangeContract(changes=[], notes="Unsupported calculator task."),
                evidence=["No matching determinstic implementation rule."],
            )
        
        changes.append(
            CodeChange(
                path="src/calculator.py",
                content=calculator_code,
                reason="Update calculator implementation.",
            )
        )
        changes.append(
            CodeChange(
                path="tests/test_calculator.py",
                content=test_code,
                reason="Update calculator tests.",
            )
        )

        return AgentResult(
            agent_name=self.name,
            status="pass",
            output=CodeChangeContract(changes=changes),
            evidence=["Generated code changes within allowed calculator files."],
        )
    
    def _ensure_import(self, test_code: str, symbol: str) -> str:
        lines = test_code.splitlines()

        for index, line in enumerate(lines):
            if line.startswith("from calculator import"):
                imports = line.replace("from calculator import", "").strip()
                names = [name.strip() for name in imports.split(",") if name.strip()]
                if symbol not in names:
                    names.append(symbol)
                lines[index] = "from calculator import " + ", ".join(sorted(names))
                return "\n".join(lines) + "\n"

        return f"from calculator import {symbol}\n\n" + test_code