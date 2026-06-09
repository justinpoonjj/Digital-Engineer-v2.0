import json 
from pathlib import Path

WORKSPACE_ROOT = Path("workspace")

class FileSafetyFilter:
    def __init__(self, map_path: Path = WORKSPACE_ROOT / "harness_map.json") -> None:
        self.map_path = map_path
        self.harness_map = json.loads(map_path.read_text(encoding="utf-8"))

    def filter_editable_files(self, candidate_files: list[str]) -> list[str]:
        protected = set(self.harness_map["protected_files"])
        editable_roots = set(self.harness_map["editable_roots"])

        safe_files = []

        for file_path in candidate_files:
            normalized  = file_path.replace("\\", "/").strip()

            if normalized in protected:
                continue

            if normalized.startswith("../") or "/../" in normalized:
                continue

            if normalized.startswith("/") or ":" in normalized:
                continue

            top_level = normalized.split("/")[0]

            if top_level not in editable_roots:
                continue

            if not normalized.endswith(".py"):
                continue

            safe_files.append(normalized)

        return sorted(set(safe_files))
    
    def get_protected_files(self) -> list[str]:
        return list(self.harness_map["protected_files"])