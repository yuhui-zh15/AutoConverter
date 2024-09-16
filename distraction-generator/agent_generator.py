from src.system import DistractionGeneratorSystem
import random

API_KEY = "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"


def get_multi_choice_question_agent(
    question: str, correct_answer: str, image_path: str
):
    system = DistractionGeneratorSystem(
        image_path=image_path,
        question=question,
        correct_answer=correct_answer,
        model="gpt-4o-2024-08-06",
        api_key=API_KEY,
    )
    distractors = list(system.generate_distractions())

    choices = [correct_answer] + distractors
    random.shuffle(choices)
    mc_question = {
        "question": question,
        "choices": choices,
        "answer": choices.index(correct_answer),
        "image_path": image_path,
    }
    return mc_question


def test_get_multi_choice_question_agent():
    question = "What is in the image?"
    correct_answer = "Motorcycle"
    image_path = "tests/image2.jpg"
    mc_question = get_multi_choice_question_agent(question, correct_answer, image_path)
    print(mc_question)


if __name__ == "__main__":
    test_get_multi_choice_question_agent()
