import gradio as gr
import pandas as pd
import json
import os
import random
random.seed(0)

def parse_multi_choice_response(response, all_choices, index2ans):
    """
    Parse the prediction from the generated response.
    Return the predicted index e.g., A, B, C, D.
    """
    response = str(response)
    for char in [',', '.', '!', '?', ';', ':', "'"]:
        response = response.strip(char)
    response = " " + response + " " # add space to avoid partial match

    index_ans = True
    ans_with_brack = False
    candidates = []
    for choice in all_choices:  # e.g., (A) (B) (C) (D)
        if f'({choice})' in response or f'{choice}. ' in response:
            candidates.append(choice)
            ans_with_brack = True

    if len(candidates) == 0:
        for choice in all_choices: # e.g., A B C D
            if f' {choice} ' in response:
                candidates.append(choice)

    # if all above doesn't get candidates, check if the content is larger than 5 tokens and try to parse the example
    if len(candidates) == 0 and len(response.split()) > 5:
        for index, ans in index2ans.items():
            if ans.lower() in response.lower():
                candidates.append(index)
                index_ans = False # it's content ans.

    if len(candidates) == 0:  # still not get answer, randomly choose one.
        pred_index = random.choice(all_choices)
    elif len(candidates) > 1:
        start_indexes = []
        if index_ans:
            if ans_with_brack: 
                for can in candidates:
                    index = response.rfind(f'({can})')
                    start_indexes.append(index) # -1 will be ignored anyway
                # start_indexes = [generated_response.index(f'({can})') for can in candidates]
            else:
                for can in candidates:
                    index = response.rfind(f" {can} ")
                    start_indexes.append(index)
        else:
            for can in candidates:
                index = response.lower().rfind(index2ans[can].lower())
                start_indexes.append(index)
        # get the last one
        pred_index = candidates[np.argmax(start_indexes)]
    else: # if only one candidate, use it.
        pred_index = candidates[0]

    return pred_index



def get_mc_score(row, use_parse = True):
    if use_parse:
        if pd.isna(row["A"]):
            return False
        response = row["prediction"]
        all_choices = []
        for i in range(9):
            if chr(65+i) in row and pd.isna(row[chr(65+i)])== False:
                all_choices.append(chr(65+i))
        index2ans = {index: row[index] for index in all_choices}
        pred_index = parse_multi_choice_response(response, all_choices, index2ans)
    else:
        pred_index = row["output"]
    return pred_index == row["answer"]

def process_json(file):
    try:
        data = json.load(file)
    except json.JSONDecodeError:
        return "Error: Invalid JSON format. Please upload a valid JSON file."

    if not isinstance(data, list):
        return "Error: JSON must be a list of records."
    
    required_fields = ['index', 'prediction']
    for record in data:
        if not all(field in record for field in required_fields):
            return f"Error: Each record must contain the following fields: {', '.join(required_fields)}"

    # Convert to DataFrame
    df = pd.DataFrame(data)
    answer_data = json.load(open("data/answer.json"))

    
    # Example categories
    general_datasets = ["SEEDBench", "MMStar", "A-OKVQA", "VizWiz", "MMVet", 
                      "VQAv2", "OKVQA"]
    reason_datasets = ["MMMU", "MathVista", "ScienceQA", "RealWorldQA",  "GQA", "MathVision"]
    ocr_datasets = ["TextVQA", "OCRVQA"]
    doc_datasets = ["AI2D", "ChartQA","DocVQA", "InfoVQA",  "TableVQABench"]
    try:
        score = df.apply(get_mc_score, axis=1) * 100
        df['score'] = score.round(2)
    except Exception as e:
        return f"Error during scoring: {str(e)}"

    # Calculate metrics for each category
    results = {}
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        category_result = category_df['score'].mean()
        results[category] = category_result

    # Compute overall and category-wise results
    overall_result = df['score'].mean()
    general_result = df[df['category'].isin(general_datasets)]['score'].mean() if len(df[df['category'].isin(general_datasets)]) > 0 else None
    reasoning_result = df[df['category'].isin(reason_datasets)]['score'].mean() if len(df[df['category'].isin(reason_datasets)]) > 0 else None
    ocr_result = df[df['category'].isin(ocr_datasets)]['score'].mean() if len(df[df['category'].isin(ocr_datasets)]) > 0 else None
    doc_result = df[df['category'].isin(doc_datasets)]['score'].mean() if len(df[df['category'].isin(doc_datasets)]) > 0 else None

    # Return as a dictionary or formatted string
    results['Overall'] = overall_result
    results['General'] = general_result
    results['Reasoning'] = reasoning_result
    results['OCR'] = ocr_result
    results['Doc & Chart'] = doc_result

    # Optionally save results or return to user
    return json.dumps(results, indent=4)

def main_gradio():
    # # read the jsonl file in /pasteur2/u/suyc/VLMEval/OE-MC/.model_results/arxiv/all/cambrian_8b_VMCBench_ALL.jsonl, drop the prediction column and save it as a json
    # raw_data = [json.loads(x) for x in open("/pasteur2/u/suyc/VLMEval/VLMEvalKit/LMUData/VMCBench-9018.jsonl")]
    # raw_data = pd.DataFrame(raw_data)
    # raw_data = raw_data.drop(columns=["image"])
    
    # raw_data = raw_data.to_dict(orient="records")
    # with open("data/answer.json", "w") as f:
    #     json.dump(raw_data, f)
    
    
    # Example JSON format string
    example_json = '''[
      {
        "index": 1,
        "prediction": "A"
      },
      {
        "index": 2,
        "prediction": "The answer is C. cat"
      }
    ]'''
    
    interface = gr.Interface(
        fn=process_json,
        inputs=gr.File(label="Upload JSON File"),
        outputs=gr.Textbox(label="Evaluation Results", interactive=False),
        title="Automated Evaluation for Multiple-Choice Questions",
        description=f"Upload a JSON file containing question index and model prediction to evaluate the performance.\n\n"
                    f"Example JSON format:\n\n{example_json}\n\n"
                    "Each record should contain the fields: 'index', 'prediction'.",
    )
    interface.launch()
    

if __name__ == "__main__":
    main_gradio()
