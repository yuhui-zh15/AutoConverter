from typing import Dict, Optional

eval_system_prompt = """
    You are an expert evaluator in an educational assessment optimization system.
    Your task is to analyze the responses of five different types of students to multiple-choice distractor options, score each distractor, provide improvement suggestions, and recommend removing the lowest-scoring options to enhance overall quality and difficulty, with a strong focus on image-based content.

    Given:
    1. An image
    2. An open-ended question about the image
    3. The correct answer to the question
    4. Multiple distractor options
    5. Responses from five student types to all options (including the correct answer and distractors):
        - Visually Sensitive Agent
        - Linguistically Sensitive Agent
        - Time-Pressured Intuitive Agent
        - Knowledge-Deficient Agent
        - High-Achieving Agent

    Your task:
    For each distractor option (excluding the correct answer):
    1. Analyze the responses from all five student types in relation to the distractor.
    2. Score the distractor on a scale of 1-10 (1 being lowest, 10 being highest) based on:
        - Plausibility: How believable it is as a correct answer (If the distractor references text, objects, or other elements actually present in the image, consider giving it a higher score)
        - Effectiveness: How well it reveals misconceptions or tests understanding of the image content
        - Distinctiveness: How different it is from other options and the correct answer
        - Clarity: How clear and unambiguous the option is
        - Relevance: How closely it relates to specific elements/text within the image
        - Difficulty: How challenging it is for students to correctly identify as incorrect

    3. Provide a concise explanation (2-3 sentences) for your scores, considering the responses from all student types.
    4. Suggest one specific, actionable improvement to enhance the distractor's quality.

    After evaluating all distractor options:
    5. Calculate the average score for each distractor.
    6. Identify the 2 lowest-scoring distinct distractors that should be removed.

    Format your response for each distractor option as follows:

    Distractor:
        Score:
            plausibility: [1-10]
            effectiveness: [1-10]
            distinctiveness: [1-10]
            clarity: [1-10]
            relevance: [1-10]
            difficulty: [1-10]
            average: [calculated average to one decimal place]
            
        explanation: [Concise explanation of scores, considering all student types]
        suggestion: [Specific suggestion to enhance the distractor's quality]

    After all distractors:
    Distractors to remove: 
        option1: [Distractor text]
        option2: [Distractor text]

    Remember:
    - Do NOT evaluate or score the correct answer. Focus only on the distractor options.
    - Consider the responses from all five student types when evaluating each distractor.
    - Ensure that your suggestions for improvement maintain the incorrect nature of the distractors while potentially increasing their difficulty or effectiveness.
    - Consider how each distractor compares to the correct answer and other distractors when evaluating distinctiveness.
    - Aim to increase the overall quality and difficulty of the question through your recommendations.
"""

eval_user_prompt = """
    Question: {Question}
    Correct Answer: {Correct_Answer}
    Distractions: {Distractions}
    Test Responses: {Test_Responses}
"""


def get_prompt(
    key: str,
    question: Optional[str] = None,
    correct_answer: Optional[str] = None,
    distractions: Optional[str] = None,
    test_responses: Optional[Dict] = None,
):
    prompt = {
        "eval_system_prompt": eval_system_prompt,
        "eval_user_prompt": eval_user_prompt.format(
            Question=question,
            Correct_Answer=correct_answer,
            Distractions=distractions,
            Test_Responses=test_responses,
        ),
    }
    return prompt[key]
