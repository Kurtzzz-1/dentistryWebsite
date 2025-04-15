import random
import sqlite3

from utils.question_class import Question, QuestionType


def execute_query(query, params=None):
    with sqlite3.connect("dentistry.db") as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
    return cursor.fetchall()


def get_topics() -> list:
    """
    Fetch all topics from the database.
    """
    query = "SELECT DISTINCT topic FROM questions"
    return [topic[0] for topic in execute_query(query)]


def get_table_names() -> list:
    """
    Fetch all table names from the database.
    """
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    return [table[0] for table in execute_query(query)]


def get_questions_for_topic(topic: str, num_questions: int) -> list[Question]:
    """
    Fetch a specified number of questions for a given topic from the database.
    """
    query = """
            SELECT id, topic, question, type
            FROM questions
            WHERE topic = ?
            """

    question_rows = execute_query(query, (topic,))
    questions: list[Question] = []

    for row in question_rows:
        question_id = row[0]
        question_text = row[2]

        if row[3] == "mcq":
            question_type = QuestionType.MULTIPLE_CHOICE
        elif row[3] == "true_false":
            question_type = QuestionType.TRUE_FALSE
        elif row[3] == "multiple_answer":
            question_type = QuestionType.MULTIPLE_ANSWER

        options_query = """
                SELECT option, is_answer
                FROM options
                WHERE question_id = ?
                """
        options_rows = execute_query(options_query, (question_id,))

        options = [option[0] for option in options_rows]
        correct_answers = [
            index for index, option in enumerate(options_rows) if option[1] == 1
        ]

        questions.append(
            Question(
                question_id=question_id,
                question=question_text,
                question_type=question_type,
                correct_answers=correct_answers,
                options=options,
                topic=row[1],
            )
        )

    return (
        random.sample(questions, num_questions)
        if len(questions) > num_questions
        else questions
    )


def get_num_questions_topic(topic: str) -> int:
    """
    Fetch the number of questions for a given topic from the database.
    """
    query = """
            SELECT COUNT(*)
            FROM questions
            WHERE topic = ?
            """

    rows = execute_query(query, (topic,))
    return rows[0][0] if rows else 0
