from abc import ABC, abstractmethod
from backend.detection.models import DetectionResult

class CodeMixDetector(ABC):
    """
    Abstract base class for all code-mix detectors.
    """

    @abstractmethod
    def detect(self, query: str) -> DetectionResult:
        """
        Analyzes the query and returns a DetectionResult detailing
        whether it's code-mixed, what languages are present, and spans.
        """
        pass
