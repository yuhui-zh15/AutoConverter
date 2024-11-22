import json
from PIL import Image
import base64
import io
from openai import OpenAI
from pydantic import BaseModel
from textwrap import dedent
from copy import deepcopy
import random


client = OpenAI(timeout=20)


def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return image


class Judgement(BaseModel):
    reasoning: str
    correctness: int
    improvement: str


class Question(BaseModel):
    reasoning: str
    distractors: list[str]


client = OpenAI(timeout=20)


def judge_multichoice_correctness_with_image(
    image_base64: str, question: str, choices: list, correct_choice: str
) -> str:
    system_prompt = f"""
    Your task is to evaluate a multiple-choice question (with accompanying image) to determine if any incorrect choices (distractors) could also be considered correct answers.

    CRITICAL: The marked correct answer MUST always be treated as valid and correct, regardless of your own assessment. Never question or evaluate the correct answer - your task is to accept it as an absolute truth and evaluate only whether other choices could also be correct.

    Score the question's correctness using this scale:
    5 - Perfect: All other choices are clearly incorrect
    4 - Good: Other choices are mostly wrong but have minor elements of correctness
    3 - Fair: At least one other choice could be partially correct
    2 - Poor: At least one other choice could be equally correct
    1 - Invalid: Multiple choices are equally valid as the correct answer

    Provide:
    1. Score (1-5)
    2. Brief explanation focusing specifically on any problematic distractor choices
    3. Suggested improvements for the problematic distractors (if applicable)

    Remember: Never analyze whether the marked correct answer is right or wrong - it is ALWAYS correct by definition. Focus exclusively on whether other choices could also be valid answers.
    """

    prompt = f"""
    Question: {question}
    Choices: {choices}
    Correct Answer: {correct_choice}
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": dedent(system_prompt),
            },  # "You are a helpful assistant."
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": dedent(prompt)},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
        ],
        response_format=Judgement,
        temperature=0,  # Set to 0 for deterministic responses
    )

    answer = response.choices[0].message.parsed.dict()
    return answer


def improve_multichoice_correctness_with_image(
    image_base64: str,
    question: str,
    choices: list,
    correct_choice: str,
    issue: str,
    improvement: str,
) -> str:
    system_prompt = """
    You are an expert in educational assessment design specializing in multiple-choice question improvement. Your task is to enhance question effectiveness by revising problematic distractors (incorrect answer choices) while maintaining the existing correct answer.

    Input Required:
    1. The complete question
    2. The current correct answer
    3. Any associated images/materials
    4. Specific feedback about problematic distractors
    5. Suggested improvements (if provided)

    Analysis Steps:
    1. Review the question content and learning objective
    2. Analyze the designated correct answer
    3. Examine the feedback regarding problematic distractors
    4. Evaluate any provided suggestions for improvement:
    - Assess if suggestions fully address the identified issues
    - Determine if suggestions align with best practices
    - Identify any gaps or weaknesses in the suggestions
    5. Develop exactly 3 improved distractors that:
    - Are plausible but clearly incorrect
    - Address the identified issues
    - Align with common student misconceptions
    - Maintain consistent format and length with other options
    - Go beyond provided suggestions when necessary for better quality

    Guidelines:
    1. Treat the marked correct answer as fixed and unchangeable
    2. Only modify distractors specifically identified as problematic
    3. Preserve any well-functioning distractors
    4. Maintain the original difficulty level of the question
    5. Use your expertise to improve upon or deviate from provided suggestions if they:
    - Are too vague or incomplete
    - Don't fully address the identified issues
    - Could be enhanced for better assessment quality
    - Miss important misconceptions or learning opportunities

    Output:
    1. Brief analysis of the distractor issues and improvement approach
    2. Three improved distractors
    """

    prompt = f"""
    Question: {question}
    Choices: {choices}
    Correct Answer: {correct_choice}
    Identified Issues: {issue}
    Suggested Improvements: {improvement}
    """

    # print(prompt)

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": dedent(system_prompt),
            },  # "You are a helpful assistant."
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": dedent(prompt)},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
        ],
        response_format=Question,
        temperature=0,  # Set to 0 for deterministic responses
    )

    distractors = response.choices[0].message.parsed.dict()
    return distractors


if __name__ == "__main__":
    annotations = json.load(open("data.json"))

    item = deepcopy(annotations[373])
    print(item)

    ################ Round 1 ################
    print("-" * 20 + " Round 1 " + "-" * 20)
    judgement = judge_multichoice_correctness_with_image(
        item["image"],
        item["question"],
        [item["A"], item["B"], item["C"], item["D"]],
        item[item["answer"]],
    )
    print(judgement)
    distractors = improve_multichoice_correctness_with_image(
        item["image"],
        item["question"],
        [item["A"], item["B"], item["C"], item["D"]],
        item[item["answer"]],
        judgement["reasoning"],
        judgement["improvement"],
    )
    print(distractors)
    answer = item[item["answer"]]
    options = distractors["distractors"] + [answer]
    random.shuffle(options)
    item["A"], item["B"], item["C"], item["D"] = options
    item["answer"] = "ABCD"[options.index(answer)]

    ################ Round 2 ################
    print("-" * 20 + " Round 2 " + "-" * 20)
    judgement = judge_multichoice_correctness_with_image(
        item["image"],
        item["question"],
        [item["A"], item["B"], item["C"], item["D"]],
        item[item["answer"]],
    )
    print(judgement)
