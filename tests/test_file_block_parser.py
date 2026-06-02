import pytest

from harness.tools.file_block_parser import FileBlockParseError, parse_file_blocks


def test_parse_single_file_block():
    raw = """FILE: src/calculator.py
```python
def add(a, b):
    return a + b
```
"""

    result = parse_file_blocks(raw)

    assert len(result.changes) == 1
    assert result.changes[0].path == "src/calculator.py"
    assert "def add" in result.changes[0].content


def test_parse_multiple_file_blocks():
    raw = """FILE: src/calculator.py
```python
def add(a, b):
    return a + b
```

FILE: tests/test_calculator.py
```python
from calculator import adds
```
"""
    result = parse_file_blocks(raw)
    assert len(result.changes) == 2
    assert result.changes[0].path == "src/calculator.py"
    assert result.changes[1].path == "tests/test_calculator.py"

def test_parser_rejects_output_without_file_block():
    with pytest.raises(FileBlockParseError):
        parse_file_blocks("Here is the code you asked for.")