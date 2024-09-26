import glob
import json
import os
import time
from typing import List, Literal

import gradio as gr
from openai import OpenAI
from pydantic import BaseModel

from prompts import acceptance_criteria, review_format


class Point(BaseModel):
    content: str
    importance: Literal["critical", "minor"]


class Review(BaseModel):
    contributions: str
    strengths: List[Point]
    weaknesses: List[Point]
    requested_changes: List[Point]
    impact_concerns: str


importance_mapping = {"critical": 2, "minor": 1}

client = OpenAI()

propose = client.beta.assistants.create(
    name="TMLR Reviewer",
    instructions="You are an expert reviewer for the Transactions on Machine Learning Research (TMLR). Your goal is to help TMLR run successfully by ensuring high-quality reviews. You are responsible for critically evaluating submissions and providing constructive feedback to authors, ensuring fairness in the review process.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

critique = client.beta.assistants.create(
    name="TMLR AE",
    instructions="You are an Action Editor for the Transactions on Machine Learning Research (TMLR). Your responsibility is to critically evaluate the performance of the reviewer. Your goal is to identify areas for improvement, ensuring that the reviewer provides high-quality and fair reviews.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

editor = client.beta.assistants.create(
    name="TMLR Editor",
    instructions="You are an editor for the Transactions on Machine Learning Research (TMLR). Your responsibility is to summarize and merge the feedback from different reviewers so that the authors can incorporate the feedback into their papers.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)


def get_response(prompt, file_id, assistant_id):
    if file_id is None:
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
    else:
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "attachments": [
                        {"file_id": file_id, "tools": [{"type": "file_search"}]}
                    ],
                }
            ]
        )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant_id
    )
    messages = list(
        client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
    )
    assert len(messages) == 1
    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"")
    return message_content.value


def get_response_simple(prompt):
    chat_completion = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o-2024-08-06",
        response_format=Review,
    )
    return chat_completion.choices[0].message.parsed.model_dump()


def parse_final(parsed, max_strengths=3, max_weaknesses=5, max_requested_changes=5):
    new_parsed = {}
    new_parsed["contributions"] = parsed["contributions"]
    new_parsed["impact_concerns"] = parsed["impact_concerns"]
    new_parsed["strengths"] = "\n".join(
        [f'- {point["content"]}' for point in parsed["strengths"][:max_strengths]]
    )
    new_parsed["weaknesses"] = "\n".join(
        [f'- {point["content"]}' for point in parsed["weaknesses"][:max_weaknesses]]
    )
    request_changes_sorted = sorted(
        parsed["requested_changes"],
        key=lambda x: importance_mapping[x["importance"]],
        reverse=True,
    )
    new_parsed["requested_changes"] = "\n".join(
        [
            f"- {point['content']} (Importance: {point['importance']})"
            for point in request_changes_sorted[:max_requested_changes]
        ]
    )
    return new_parsed


def run_once(file_path):
    message_file = client.files.create(file=open(file_path, "rb"), purpose="assistants")

    prompt1 = f"Could you review this paper? Ensure that your review is constructive, actionable, and aligns with the standards of TMLR.\n\nHere is the acceptance criteria of TMLR:\n\n```{acceptance_criteria}```\n\nHere is the review format you should follow:\n\n```{review_format}```"
    response1_first = get_response(prompt1, message_file.id, propose.id)
    response1_second = get_response(prompt1, message_file.id, propose.id)

    prompt2 = f"Could you combine feedback from two reviewers into one long review in a consistent format? Make sure each point is as detailed as the individual review. Do not worry about the review length. Remove duplicate points.\n\nHere is the review 1:\n\n```{response1_first}```\n\nHere is the review 2:\n\n```{response1_second}```\n\nPlease use the original TMLR review format."
    response2 = get_response(prompt2, None, editor.id)

    prompt3 = f"Could you evaluate this review written by a reviewer and provide suggested improvements? Identify and provide detailed feedback on any shortcomings, biases, or areas where the reviewer's critique could be improved. Ensure that your feedback is constructive, actionable, and aligns with the standards of TMLR.\n\nHere is the review from the reviewer:\n\n```{response2}```"
    response3 = get_response(prompt3, message_file.id, critique.id)

    prompt4 = f"Could you improve the review of this paper?\n\nHere is the review wrote previously:\n\n```{response2}```\n\nHere are some suggestions for improvement from the Action Editor (AE):\n\n```{response3}```\n\nOutput the improved review only. Please still use the original TMLR review format."
    response4 = get_response(prompt4, message_file.id, propose.id)

    prompt5 = f"Could you parse the review into the correct format?\n\nHere is the review written previously:\n\n```{response4}```\n\nPlease keep the original Markdown tags, like bold (two asterisks) or linebreak. After parsing the importance, remove the original importance tag."
    response5 = get_response_simple(prompt5)

    parsed = parse_final(response5)

    return (
        response1_first,
        response1_second,
        response2,
        response3,
        response4,
        response5,
        parsed,
    )


def main():
    for file_path in glob.glob("./papers/*.pdf"):
        try:
            print(file_path)
            output_path = file_path.replace(".pdf", "_v7.json")
            responses = run_once(file_path)
            json.dump(responses, open(output_path, "w"))
        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    main()