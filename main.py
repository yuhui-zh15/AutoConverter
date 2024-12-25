import base64
import io
import random
from textwrap import dedent

import gradio as gr
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel

from prompts import (
    concept_generation_system_prompt,
    data_processing_generation_system_prompt,
    evaluator_system_prompt,
    fusion_generation_system_prompt,
    question_bias_generation_system_prompt,
    reasoning_generation_system_prompt,
    refine_system_prompt_concept,
    refine_system_prompt_data,
    refine_system_prompt_question_bias,
    refine_system_prompt_reason,
    refine_system_prompt_visual,
    refiner_system_prompt,
    review_system_prompt,
    visual_interpretation_generation_system_prompt,
)


class Distractor(BaseModel):
    text: str
    reason: str


class Distractors(BaseModel):
    distractors: list[Distractor]


class Comment(BaseModel):
    option: str
    comment: str


class CommentFormat(BaseModel):
    comments: list[Comment]


class Judgement(BaseModel):
    reasoning: str
    correctness: int
    improvement: str


class Question(BaseModel):
    reasoning: str
    distractors: list[str]


def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return image


def get_reply(client, system_prompt, user_prompt, image_base64, output_format):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": dedent(system_prompt)},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": dedent(user_prompt)},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            },
        ],
        response_format=output_format,
        # temperature=0,  # Set to 0 for deterministic responses
    )
    parsed_output = completion.choices[0].message.parsed.dict()
    return parsed_output


def convert_to_multi_choice(client, question, answer, image_base64, reviewer):
    user_prompt = f"""
    Question: {question}
    Correct Answer: {answer}
    """

    distractors_concept = get_reply(
        client, concept_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]
    distractors_reasoning = get_reply(
        client,
        reasoning_generation_system_prompt,
        user_prompt,
        image_base64,
        Distractors,
    )["distractors"]
    distractors_visual_interpretation = get_reply(
        client,
        visual_interpretation_generation_system_prompt,
        user_prompt,
        image_base64,
        Distractors,
    )["distractors"]
    distractors_data_processing = get_reply(
        client,
        data_processing_generation_system_prompt,
        user_prompt,
        image_base64,
        Distractors,
    )["distractors"]
    distractors_question_bias = get_reply(
        client,
        question_bias_generation_system_prompt,
        user_prompt,
        image_base64,
        Distractors,
    )["distractors"]
    # print(distractors_concept)

    if reviewer:
        user_prompt = """
            Question: {question}
            Correct Answer: {answer}
            Distractions and Reasonings: {distractors}
        """
        reviews_concept = get_reply(
            client,
            review_system_prompt.format(type="conceptual"),
            user_prompt.format(
                question=question, answer=answer, distractors=distractors_concept
            ),
            image_base64,
            CommentFormat,
        )["comments"]
        reviews_reasoning = get_reply(
            client,
            review_system_prompt.format(type="reasoning"),
            user_prompt.format(
                question=question, answer=answer, distractors=distractors_reasoning
            ),
            image_base64,
            CommentFormat,
        )["comments"]
        reviews_visual_interpretation = get_reply(
            client,
            review_system_prompt.format(type="visual interpretation"),
            user_prompt.format(
                question=question,
                answer=answer,
                distractors=distractors_visual_interpretation,
            ),
            image_base64,
            CommentFormat,
        )["comments"]
        reviews_data_processing = get_reply(
            client,
            review_system_prompt.format(type="data processing"),
            user_prompt.format(
                question=question,
                answer=answer,
                distractors=distractors_data_processing,
            ),
            image_base64,
            CommentFormat,
        )["comments"]
        reviews_question_bias = get_reply(
            client,
            review_system_prompt.format(type="question bias"),
            user_prompt.format(
                question=question, answer=answer, distractors=distractors_question_bias
            ),
            image_base64,
            CommentFormat,
        )["comments"]
        # print(reviews_concept)

        user_prompt = """
            Question: {question}
            Correct Answer: {answer}
            Distractions and Reviewer Comments: {reviews}
        """
        distractors_concept = get_reply(
            client,
            refine_system_prompt_concept,
            user_prompt.format(
                question=question, answer=answer, reviews=reviews_concept
            ),
            image_base64,
            Distractors,
        )["distractors"]
        distractors_reasoning = get_reply(
            client,
            refine_system_prompt_reason,
            user_prompt.format(
                question=question, answer=answer, reviews=reviews_reasoning
            ),
            image_base64,
            Distractors,
        )["distractors"]
        distractors_visual_interpretation = get_reply(
            client,
            refine_system_prompt_visual,
            user_prompt.format(
                question=question, answer=answer, reviews=reviews_visual_interpretation
            ),
            image_base64,
            Distractors,
        )["distractors"]
        distractors_data_processing = get_reply(
            client,
            refine_system_prompt_data,
            user_prompt.format(
                question=question, answer=answer, reviews=reviews_data_processing
            ),
            image_base64,
            Distractors,
        )["distractors"]
        distractors_question_bias = get_reply(
            client,
            refine_system_prompt_question_bias,
            user_prompt.format(
                question=question, answer=answer, reviews=reviews_question_bias
            ),
            image_base64,
            Distractors,
        )["distractors"]
        # print(distractors_concept)

    distractors = (
        distractors_concept
        + distractors_reasoning
        + distractors_visual_interpretation
        + distractors_data_processing
        + distractors_question_bias
    )

    user_prompt = f"""
    Question: {question}
    Correct Answer: {answer}
    All Distractors: {distractors}
    """

    distractors = get_reply(
        client, fusion_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]

    return distractors


def judge_multichoice_correctness_with_image(
    client, question, choices, answer, image_base64
):
    user_prompt = f"""
    Question: {question}
    Choices: {choices}
    Correct Answer: {answer}
    """
    response = get_reply(
        client,
        evaluator_system_prompt,
        user_prompt,
        image_base64,
        Judgement,
    )
    return response


def improve_multichoice_correctness_with_image(
    client,
    question,
    choices,
    answer,
    issue,
    improvement,
    image_base64,
):
    user_prompt = f"""
    Question: {question}
    Choices: {choices}
    Correct Answer: {answer}
    Identified Issues: {issue}
    Suggested Improvements: {improvement}
    """

    response = get_reply(
        client,
        refiner_system_prompt,
        user_prompt,
        image_base64,
        Question,
    )
    return response


def process_one_question(api_key, image, question, answer, components):
    reviewer = "Reviewer" in components
    refiner = "Refiner" in components

    pil_image = Image.fromarray(image)

    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    random.seed(1234)
    client = OpenAI(api_key=api_key)
    distactors = convert_to_multi_choice(
        client, question, answer, image_base64, reviewer
    )

    choices = [item["text"] for item in distactors] + [answer]
    random.shuffle(choices)

    if refiner:
        judgement = judge_multichoice_correctness_with_image(
            client, question, choices, answer, image_base64
        )
        distractors = improve_multichoice_correctness_with_image(
            client,
            question,
            choices,
            answer,
            judgement["reasoning"],
            judgement["improvement"],
            image_base64,
        )

        choices = distractors["distractors"] + [answer]
        random.shuffle(choices)

    output = f"Question: {question}\n\nA. {choices[0]}\nB. {choices[1]}\nC. {choices[2]}\nD. {choices[3]}\n\nAnswer: {'ABCD'[choices.index(answer)]}"
    return output


def main_gradio():
    interface = gr.Interface(
        fn=process_one_question,
        inputs=[
            gr.Textbox(label="OpenAI API Key"),
            gr.Image(label="Upload an Image"),
            gr.Textbox(label="Question"),
            gr.Textbox(label="Answer"),
            gr.CheckboxGroup(["Reviewer", "Refiner"], label="Components"),
        ],
        outputs=gr.Textbox(label="Output"),
        title="AutoConverter: Automated Generation of Challenging Multiple-Choice Questions for Vision Language Model Evaluation",
    )
    interface.launch()


if __name__ == "__main__":
    main_gradio()
