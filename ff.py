from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Optional
import pandas as pd
import io, os
import json


class MCQItem(BaseModel):
    question: str = Field(..., description="The question text")
    options: Optional[Dict[str, str]] = Field(..., description="Options with keys A-D")
    answer : str = Field(..., description="The answer text")
    explanation: Optional[str] = Field(..., description="The explanation for the answer")

class MCQSet(BaseModel):
    mcqs: Optional[Dict[str, MCQItem]] = Field(..., description="A dictionary of MCQs keyed by question number (e.g., '1', '2')")



def generate_mcqs(mode: str, content= '', number=None, topic=None) -> MCQSet:
    """    Generate MCQs based on the given topic and number of questions.
    Args:
        topic (str): The topic for the MCQs.
        number (int): The number of MCQs to generate."""

    # ✅ Create OpenAI Client (Responses mode)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # ✅ Prompt
    p1 = """
    Your task is to convert the MCQs in the text you receive into the format below.
    The text you receive can be a test sheet, a PDF with MCQs, or any other unstructured text. Ignore other parts of the text that are not MCQs.
    Make sure that the questions you extract are sound and the explanations are correct.

    You MUST respond with a single, valid JSON object.
    The JSON object should have a key named "mcqs".
    The value of "mcqs" should be another JSON object where each key is a question number as a string (e.g., "1", "2", ...).
    The value for each question number should be an object containing:
    1. "question": A string with the question text.
    2. "options": An object where keys are "A", "B", "C", "D" and values are the option texts.
    3. "answer": A string indicating the correct option key (e.g., "A").
    4. "explanation": A string with the explanation for the answer.
    Do not include any explanation or text outside the JSON.
    """

    p2 = f"""
    Your task is to generate {number} MCQs about {topic} with sensible options in the format given below
    You MUST respond with a single, valid JSON object.
    The JSON object should have a key named "mcqs".
    The value of "mcqs" should be another JSON object where each key is a question number as a string (e.g., "1", "2", ...).
    The value for each question number should be an object containing:
    1. "question": A string with the question text.
    2. "options": An object where keys are "A", "B", "C", "D" and values are the option texts.
    3. "answer": A string indicating the correct option key (e.g., "A").
    4. "explanation": A string with the explanation for the answer.
    Do not include any explanation or text outside the JSON.

    """

    if mode == "parse":
        system = p1
    elif mode == "generate":
        system = p2
    else:
        raise ValueError("Invalid mode. Use 'parse' or 'generate'.")
    
    # ✅ Load unstructured MCQ text from file
    

    ##✅ Parse directly to structured object using the SDK
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": content}
        ],
        response_format=MCQSet
    )


    mcqs = response
    mcqs = (mcqs.choices[0].message.content)


    mcqs_data = json.loads(mcqs)

    rows = []
    for qid, item in mcqs_data["mcqs"].items():
        row = {
            "ID": qid,
            "Question": item["question"],
            "Option A": item["options"]["A"],
            "Option B": item["options"]["B"],
            "Option C": item["options"]["C"],
            "Option D": item["options"]["D"],
            "Answer": item["answer"],
            "Explanation": item["explanation"]
        }
        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)

    output = io.BytesIO()
    df.to_excel(output, index=False)

    output.seek(0)  # Rewind the buffer
    return output