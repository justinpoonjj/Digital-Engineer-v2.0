import json
from dataclasses import dataclass
from pathlib import Path

WORKSPACE_ROOT = Path("workspace")

@dataclass
class LocalizationResult:
    feature_name: str
    source_files: list[str]
    test_files: list[str]
    validation_profile: str
    matched_keywords: list[str]

class FileLocalizer: 
    def __init__(self, map_path: Path = WORKSPACE_ROOT / "harness_map.json") -> None:
        self.map_path = map_path

    def localize(self, user_request: str) -> LocalizationResult:
        harness_map = json.loads(self.map_path.read_text(encoding="utf-8"))
        request = user_request.lower()

        best_match = None
        best_keywords = []

        for feature_name, feature in harness_map["features"].items():
            matched = [
                keyword for keyword in feature["keywords"]
                if keyword.lower() in request
            ]

            if len(matched) > len(best_keywords):
                best_match = (feature_name, feature)
                best_keywords = matched

        if best_match is None:
            raise ValueError(f"Could not localize files for request: {user_request}")
        
        feature_name, feature = best_match

        return LocalizationResult(
            feature_name=feature_name,
            source_files=feature["source_files"],
            test_files=feature["test_files"],
            validation_profile=feature["validation_profile"],
            matched_keywords=best_keywords,
        )