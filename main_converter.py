# %%
import sys
sys.path.append('/pasteur2/u/yuhuiz/CVPR/AutoConverter/VLMEvalKit')

from vlmeval import *

######################### MMMU #########################
dataset_name = 'MMMU_DEV_VAL'
dataset = build_dataset(dataset_name)
def get_n_choice(item):
    choices = [item[idx] for idx in "ABCDEFGHI"]
    choices = [choice for choice in choices if choice == choice]
    return len(choices)
dataset_4choices = [item for item in dataset if get_n_choice(item) == 4 and isinstance(item["image_path"], str)]
print(f"dataset: {dataset_name}, total: {len(dataset)}, 4 choices: {len(dataset_4choices)}")

######################### MathVista #########################
# dataset_name = 'MathVista_MINI'
# dataset = build_dataset(dataset_name)
# def get_n_choice(item):
#     try:
#         choices = eval(item["choices"])
#         return len(choices)
#     except:
#         return 0
# dataset_4choices = [item for item in dataset if get_n_choice(item) == 4]
# print(f"dataset: {dataset_name}, total: {len(dataset)}, 4 choices: {len(dataset_4choices)}")

import json
with open(f"data/{dataset_name}_4choices_original.jsonl", 'w') as f:
    for item in dataset_4choices:
        item["index"] = int(item["index"])
        f.write(json.dumps(item) + '\n')

# %%
from pydantic import BaseModel
from openai import OpenAI
from textwrap import dedent
from PIL import Image
import base64
import io


client = OpenAI()

class Distractor(BaseModel):
    text: str
    reason: str

class Distractors(BaseModel):
    distractors: list[Distractor]


def base64_to_image(base64_str):
    """
    Convert a base64 string to a PIL Image.
    
    Args:
        base64_str (str): The base64 encoded image string.
        
    Returns:
        PIL.Image.Image: The image object.
    """
    # Decode the base64 string into bytes
    image_data = base64.b64decode(base64_str)
    
    # Convert bytes into a PIL image
    image = Image.open(io.BytesIO(image_data))
    
    return image


# def convert_to_multi_choice(item):
#     question = item["question"]
#     answer = item[item["answer"]]
#     image_base64 = item["image"]

#     system_prompt = "You are a helpful assistant."
#     user_prompt = f"""Please generate 3 distractors for this question given the image:

#     Question: {question}
#     Answer: {answer}
#     """

#     completion = client.beta.chat.completions.parse(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": dedent(system_prompt)},
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": dedent(user_prompt)},
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": f"data:image/png;base64,{image_base64}"},
#                     },
#                 ],
#             },
#         ],
#         response_format=Distractors,
#     )

#     distractors = completion.choices[0].message.parsed.dict()
#     choices = [answer] + [distractor["text"] for distractor in distractors["distractors"]]
#     reasons = [None] + [distractor["reason"] for distractor in distractors["distractors"]]
#     multi_choice_questions = {
#         "question": question,
#         "choices": choices,
#         "reasons": reasons,
#         "answer": answer,
#     }
#     return multi_choice_questions


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




from prompts import concept_generation_system_prompt, reasoning_generation_system_prompt, visual_interpretation_generation_system_prompt, data_processing_generation_system_prompt, question_bias_generation_system_prompt, fusion_generation_system_prompt, confuse_system_prompt
def convert_to_multi_choice(item):
    question = item["question"]
    answer = item[item["answer"]]
    image_base64 = item["image"]

    user_prompt = f"""
    Question: {question}
    Correct Answer: {answer}
    """

    distractors_concept = get_reply(concept_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]
    # print(distractors_concept)
    distractors_reasoning = get_reply(reasoning_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]
    distractors_visual_interpretation = get_reply(visual_interpretation_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]
    distractors_data_processing = get_reply(data_processing_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]
    distractors_question_bias = get_reply(question_bias_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]

    # user_prompt = f"""
    # Question: {question}
    # Answer: {answer}

    # Given the distractors generated already:
    # ```{distractors_concept}```
    
    # Please think carefully about how to improve these distractors and refine these distractors.
    # """
    # distractors_concept = get_reply(concept_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]
    # print(distractors_concept)
    

    distractors = distractors_concept + distractors_reasoning + distractors_visual_interpretation + distractors_data_processing + distractors_question_bias
    


    user_prompt = f"""
    Question: {question}
    Correct Answer: {answer}
    All Distractors: {distractors}
    """

    distractors = get_reply(fusion_generation_system_prompt, user_prompt, image_base64, Distractors)["distractors"]

    # distractors = [distractor["text"] for distractor in distractors]
    # user_prompt = f"""
    #     Question: {question}
    #     Options: {distractors}
    # """

    # distractors = get_reply(confuse_system_prompt, user_prompt, image_base64, Distractors)["distractors"]

    choices = [answer] + [distractor["text"] for distractor in distractors]
    reasons = [None] + [distractor["reason"] for distractor in distractors]
    multi_choice_questions = {
        "question": question,
        "choices": choices,
        "reasons": reasons,
        "answer": answer,
    }
    return multi_choice_questions

# %%
convert_to_multi_choice(dataset_4choices[0])

# %%
import random
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import trange, tqdm

random.seed(1234)

# Deep copy the dataset
dataset_4choices_naive = copy.deepcopy(dataset_4choices)

# Function to process a single question item
def process_item(qidx):
    item = dataset_4choices_naive[qidx]
    multi_choice_questions = convert_to_multi_choice(item)

    choices = multi_choice_questions["choices"]
    answer = item[item["answer"]]
    random.shuffle(choices)
    answer_idx = choices.index(answer)

    for idx in range(len(choices)):
        item[chr(65 + idx)] = choices[idx]
    item["answer"] = chr(65 + answer_idx)

    return qidx, item

# Parallelize using ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    # Submit tasks for parallel execution, associating futures with their indices
    futures = [executor.submit(process_item, qidx) for qidx in range(len(dataset_4choices_naive))]

    # Create progress bar and track as futures complete
    results = []
    for future in tqdm(as_completed(futures), total=len(futures)):
        results.append(future.result())

    # Sort results to maintain the original order
    results = sorted(results, key=lambda x: x[0])

# save results to data/MMMU_DEV_VAL_4choices_20241023_0056.jsonl
import json
output_filename = f"data/{dataset_name}_4choices_20241102_2028.jsonl"
with open(output_filename, 'w') as f:
    for _, item in results:
        item["index"] = int(item["index"])
        f.write(json.dumps(item) + '\n')

# %%
# from matplotlib import pyplot as plt
# from collections import Counter

# non_mc_dataset = [item for item in dataset if item["answer"] not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
# mc_dataset = [item for item in dataset if item["answer"] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

# def compute_n_choice(item):
#     choices = [item[idx] for idx in "ABCDEFGHI"]
#     # remove nan
#     choices = [choice for choice in choices if choice == choice]
#     return len(choices)


# n_choices = [compute_n_choice(item) for item in dataset]
# len(non_mc_dataset), len(mc_dataset)

# plt.bar(Counter(n_choices).keys(), Counter(n_choices).values())
# plt.title("Number of choices in MMMU")

# %%



