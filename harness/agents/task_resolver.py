from harness.contracts import TaskContract
from harness.localization.file_localizer import FileLocalizer
from harness.localization.safety_filter import FileSafetyFilter

#This is intentionally deterministic for now. Later, you can use an LLM for task resolution.

class TaskResolverAgent: 
    name = "task_resolver"

    def __init__(self) -> None: 
        self.localizer = FileLocalizer()
        self.safety_filter = FileSafetyFilter()

    def resolve(self, user_request: str) -> TaskContract:
        localization = self.localizer.localize(user_request)

        candidate_files = localization.source_files + localization.test_files
        safe_allowed_files = self.safety_filter.filter_editable_files(candidate_files)

        return TaskContract(
            task_id=f"{localization.feature_name}-task",
            user_request=user_request,
            resolved_task=self._resolve_task_text(user_request),
            task_type=f"{localization.feature_name}_feature",
            required_files=safe_allowed_files,
            allowed_files=safe_allowed_files,
            forbidden_files=self.safety_filter.get_protected_files(),
            validation_profile=localization.validation_profile,
            completion_evidence=[
                f"pytest {' '.join(localization.test_files)} passes",
                f"ruff check {' '.join(safe_allowed_files)} passes",
            ],
        )

    def _resolve_task_text(self, user_request:str) -> str:
        request = user_request.lower()

        if "subtract" in request or "subtraction" in request:
            return "Add a subtract(a, b) function to the calculator and test it."

        if "multiply" in request or "multiplication" in request:
            return "Add a multiply(a, b) function to the calculator and test it."

        if "divide" in request or "division" in request:
            return "Add a divide(a, b) function to the calculator and test it."

        if "add" in request or "addition" in request:
            return "Add an add(a, b) function to the calculator and test it."


        return user_request