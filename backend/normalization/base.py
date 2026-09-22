from abc import ABC, abstractmethod
from backend.normalization.models import NormalizationResult
from backend.detection.models import DetectionResult

class QueryNormalizer(ABC):
    """
    Abstract base class for query normalization.
    """

    @abstractmethod
    def normalize(self, query: str, detection_result: DetectionResult) -> NormalizationResult:
        """
        Takes a raw query and its detection result, and returns
        a normalized English query if code-mixing is present.
        """
        pass
