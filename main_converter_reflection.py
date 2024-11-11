from pydantic import BaseModel
from openai import OpenAI
from textwrap import dedent
from PIL import Image
import base64
import io
from prompts import (
    concept_generation_system_prompt,
    reasoning_generation_system_prompt,
    visual_interpretation_generation_system_prompt,
    data_processing_generation_system_prompt,
    question_bias_generation_system_prompt,
    fusion_generation_system_prompt,
    confuse_system_prompt,
    refine_system_prompt_concept,
    refine_system_prompt_reason,
    refine_system_prompt_visual,
    refine_system_prompt_data,
    refine_system_prompt_question_bias,
    review_system_prompt,
)


client = OpenAI()


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


def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return image


def get_reply(system_prompt, user_prompt, image_base64, output_format):
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
    )
    parsed_output = completion.choices[0].message.parsed.dict()
    return parsed_output


def convert_to_multi_choice(question, answer, image_base64):
    user_prompt = f"""
    Question: {question}
    Correct Answer: {answer}
    """

    distractors_concept = get_reply(
        concept_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]
    distractors_reasoning = get_reply(
        reasoning_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]
    distractors_visual_interpretation = get_reply(
        visual_interpretation_generation_system_prompt,
        user_prompt,
        image_base64,
        Distractors,
    )["distractors"]
    distractors_data_processing = get_reply(
        data_processing_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]
    distractors_question_bias = get_reply(
        question_bias_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]
    # print(distractors_concept)

    ############ Round 1 ############
    user_prompt = """
        Question: {question}
        Correct Answer: {answer}
        Distractions and Reasonings: {distractors}
    """
    reviews_concept = get_reply(
        review_system_prompt.format(type="conceptual"),
        user_prompt.format(
            question=question, answer=answer, distractors=distractors_concept
        ),
        image_base64,
        CommentFormat,
    )["comments"]
    reviews_reasoning = get_reply(
        review_system_prompt.format(type="reasoning"),
        user_prompt.format(
            question=question, answer=answer, distractors=distractors_reasoning
        ),
        image_base64,
        CommentFormat,
    )["comments"]
    reviews_visual_interpretation = get_reply(
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
        review_system_prompt.format(type="data processing"),
        user_prompt.format(
            question=question, answer=answer, distractors=distractors_data_processing
        ),
        image_base64,
        CommentFormat,
    )["comments"]
    reviews_question_bias = get_reply(
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
        refine_system_prompt_concept,
        user_prompt.format(question=question, answer=answer, reviews=reviews_concept),
        image_base64,
        Distractors,
    )["distractors"]
    distractors_reasoning = get_reply(
        refine_system_prompt_reason,
        user_prompt.format(question=question, answer=answer, reviews=reviews_reasoning),
        image_base64,
        Distractors,
    )["distractors"]
    distractors_visual_interpretation = get_reply(
        refine_system_prompt_visual,
        user_prompt.format(
            question=question, answer=answer, reviews=reviews_visual_interpretation
        ),
        image_base64,
        Distractors,
    )["distractors"]
    distractors_data_processing = get_reply(
        refine_system_prompt_data,
        user_prompt.format(
            question=question, answer=answer, reviews=reviews_data_processing
        ),
        image_base64,
        Distractors,
    )["distractors"]
    distractors_question_bias = get_reply(
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
        fusion_generation_system_prompt, user_prompt, image_base64, Distractors
    )["distractors"]

    return distractors


if __name__ == "__main__":
    import sys

    sys.path.append("/pasteur2/u/yuhuiz/CVPR/AutoConverter/VLMEvalKit")

    from vlmeval import build_dataset

    dataset_name = "MMMU_DEV_VAL"
    dataset = build_dataset(dataset_name)

    def get_n_choice(item):
        choices = [item[idx] for idx in "ABCDEFGHI"]
        choices = [choice for choice in choices if choice == choice]
        return len(choices)

    dataset_4choices = [
        item
        for item in dataset
        if get_n_choice(item) == 4 and isinstance(item["image_path"], str)
    ]
    print(
        f"dataset: {dataset_name}, total: {len(dataset)}, 4 choices: {len(dataset_4choices)}"
    )

    item = dataset_4choices[0]
    question = item["question"]
    answer = item[item["answer"]]
    image_base64 = item["image"]
    distactors = convert_to_multi_choice(question, answer, image_base64)
    print(distactors)
