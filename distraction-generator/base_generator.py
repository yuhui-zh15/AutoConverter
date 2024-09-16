from src.get_reply import get_reply
from pydantic import BaseModel
from typing import List
import random


class Distractors(BaseModel):
    distractors: List[str]


def get_multi_choice_question_baseline(
    question: str, correct_answer: str, image_path: str
):
    input_data = """
        question: {question}
        correct_answer: {correct_answer}
    """
    input_data = input_data.format(question=question, correct_answer=correct_answer)
    reply = get_reply(
        image_path,
        "gpt-4o-2024-08-06",
        "You are a helpful assistant. Please generate 3 distractors for the following question based on the image, question and correct answer.",
        input_data,
        Distractors,
    )
    distractors = reply.parsed.distractors
    choices = [correct_answer] + distractors
    random.shuffle(choices)
    mc_question = {
        "question": question,
        "choices": choices,
        "answer": choices.index(correct_answer),
        "image_path": image_path,
    }
    return mc_question


def test_get_multi_choice_question_baseline():
    question = "What is in the image?"
    correct_answer = "Motorcycle"
    image_path = "tests/image2.jpg"
    mc_question = get_multi_choice_question_baseline(
        question, correct_answer, image_path
    )
    print(mc_question)


if __name__ == "__main__":
    test_get_multi_choice_question_baseline()
