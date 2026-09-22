from typing import Protocol
from backend.evaluation.models import EvaluationResult

class FaithfulnessJudge(Protocol):
    """
    Interface for evaluating the faithfulness of a generated answer against the retrieved context.
    """
    def evaluate(self, answer: str, context: str) -> EvaluationResult:
        """
        Evaluate the faithfulness of the answer based on the context.

        Args:
            answer (str): The generated answer.
            context (str): The retrieved context.

        Returns:
            EvaluationResult: The evaluation score and hallucination flag.
        """
        ...
