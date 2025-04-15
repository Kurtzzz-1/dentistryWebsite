import enum
from dataclasses import dataclass


class QuestionType(enum.Enum):
    MULTIPLE_CHOICE = 1
    TRUE_FALSE = 2
    MULTIPLE_ANSWER = 3


# TODO: Add the ability to have multiple correct answers - Addressed
@dataclass
class Question:
    question_id: int
    question: str
    question_type: QuestionType
    correct_answers: list[int]  # Changed from answer_index: int
    options: list[str]
    topic: str
