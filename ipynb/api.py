import string
from PIL import Image
import json
from tqdm import tqdm
import random
import click
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from anthropic import Anthropic
from openai import OpenAI
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pandas as pd
from ast import literal_eval
# def load_data(data_path, class_path, split, seed):
#     data = [json.loads(line) for line in open(data_path)]
#     data = [item for item in data if item["split"] == split]

#     random.seed(seed)
#     random.shuffle(data)
#     classes = json.load(open(class_path))

#     print(f"{len(data)=}")

#     return data, classes

def load_data(data_path):
    data = pd.read_csv(data_path, sep='\t')
    data = data.to_dict('records')
    return data

def process_with_gemini(item, processed_idxs):
    if item["index"] in processed_idxs:
        return None

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    
    
    question = create_question(item)
    
    output = None
    # print("Generate: ", item['index'])
    # for i in range(3):
    try:
        image = Image.open(f"/pasteur2/u/suyc/VLMEval/VLMEvalKit/LMUData/images/VMCBench-9450/{item['index']}.jpg")
        response = model.generate_content([question, image],
                                          safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    })
        output = response.text
        # print("Generated: ", item['index'], 'prediction: ', output)
    except Exception as e:
        print(e, item['index'])
    if output is None:
        print("No response", item['index'])
        return None
    
    item["question"] = question
    item["prediction"] = output
    new_item = {
        "index": item["index"],
        "question": item["question"],
        "A": item["A"],
        "B": item["B"],
        "C": item["C"],
        "D": item["D"],
        "answer": item["answer"],
        "prediction": item["prediction"],
    }
    return new_item

def process_with_claude(item, processed_idxs):
    if item["index"] in processed_idxs:
        return None
    try:
        if isinstance(literal_eval(item["image"]), list):
            item["image"] = literal_eval(item["image"])[0]
    except:
        pass
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # with open(item["image"], "rb") as image_file:
    #     binary_data = image_file.read()
    #     base_64_encoded_data = base64.b64encode(binary_data)
    #     base64_string = base_64_encoded_data.decode("utf-8")
    
    question = create_question(item)
    question += "Please do not add any rationale or explanation. Only output the choice letter.\n"
    output = None
    # for i in range(3):
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": item['image'],
                            },
                        },
                        {"type": "text", "text": question},
                    ],
                }
            ],
        )
        output = response.content[0].text
    except Exception as e:
        print(item['index'],": ", e)
        # time.sleep(60)
        # continue
    if output is None:
        print("No response", item['index'])
        return None
    
    item["question"] = question
    item["prediction"] = output
    new_item = {
        "index": item["index"],
        "question": item["question"],
        "A": item["A"],
        "B": item["B"],
        "C": item["C"],
        "D": item["D"],
        "answer": item["answer"],
        "prediction": item["prediction"],
    }
    return new_item

def process_with_gpt4v(item, classes, including_label, n_labels, processed_idxs):
    if item["index"] in processed_idxs:
        return None

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    img_path = item["image"]
    base64_image = encode_image(img_path)
    
    question = create_question(item, classes, including_label, n_labels)
    
    output = None
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        ],
                    },
                ],
            )
            output = response.choices[0].message.content
        except Exception as e:
            print(e, item, f"{i} times retrying...")
            time.sleep(60)
            continue
    if output is None:
        print("No response", item)
        return None
    
    item["question"] = question
    item["output"] = output
    return item

def create_question(line):
    question = line['question']
    options = {
        cand: line[cand]
        for cand in string.ascii_uppercase
        if cand in line and not pd.isna(line[cand])
    }
    options_prompt = 'Options:\n'
    for key, item in options.items():
        options_prompt += f'{key}. {item}\n'
    prompt = ''
    prompt += f'Question: {question}\n'
    if len(options):
        prompt += options_prompt
        # prompt += 'Please select the correct answer from the options above. \n'
        prompt += "Answer with the option's letter from the given choices directly. \n"
        # prompt += 'Think step by step and then add the final answer in the format of \"The answer is (X)\" at the end.'

    
    return prompt

@click.command()
@click.option("--data_path", default="/pasteur2/u/suyc/VLMEval/VLMEvalKit/LMUData/VMCBench-9450.tsv")
@click.option("--output_path", default="outputs/vmcbench_outputs")
@click.option("--api", type=click.Choice(['gemini', 'claude', 'gpt4v']), default='gemini')
@click.option("--threads", default=16)
@click.option("--data_limit", default=10000)
def main(data_path, output_path, api, threads, data_limit):
    data = load_data(data_path)
    data = data[:data_limit]
    output_path = f"{output_path}_{api}.jsonl"
    if os.path.exists(output_path):
        outputs = [json.loads(line) for line in open(output_path)]
        processed_idxs = set([item["index"] for item in outputs])
    else:
        processed_idxs = set()

    with ThreadPoolExecutor(max_workers=threads) as executor, open(output_path, "a") as f:
        futures = []
        for item in data:
            if api == 'gemini':
                futures.append(executor.submit(process_with_gemini, item, processed_idxs))
            elif api == 'claude':
                futures.append(executor.submit(process_with_claude, item, processed_idxs))
            elif api == 'gpt4v':
                futures.append(executor.submit(process_with_gpt4v, item, processed_idxs))
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            result = future.result()
            if result:
                f.write(json.dumps(result) + "\n")
                f.flush()

if __name__ == "__main__":
    main()