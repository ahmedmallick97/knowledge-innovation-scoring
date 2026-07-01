from fastapi import FastAPI
from pydantic import BaseModel
from openai import AzureOpenAI
import json
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
# azure open ai config


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

# -----------------------------
# LOAD DATASET
# -----------------------------

with open("data.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# -----------------------------
# REQUEST MODELS
# -----------------------------

class InterviewInput(BaseModel):
    user_input: str
    history: list = []

class TranscriptInput(BaseModel):
    transcript: str

# -----------------------------
# LLM CALL
# -----------------------------

def call_llm(messages):

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
        #temperature=1
    )

    return response.choices[0].message.content


# -----------------------------
# HELPER: CLEAN JSON RESPONSE
# -----------------------------

def clean_json_response(text):

    if not text:
        return {}

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        return json.loads(text)

    except Exception:
        return {
            "raw_response": text
        }

# -----------------------------
# RETRIEVAL
# -----------------------------

def retrieve_similar(query):

    query = query.lower()

    scored = []

    for item in dataset:

        text = (
            item["problem"]
            + " "
            + item["solution"]
            + " "
            + item["impact"]
            + " "
            + item["context"]
        ).lower()

        score = sum(
            1
            for word in query.split()
            if word in text
        )

        scored.append((score, item))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [s[1] for s in scored[:3]]

# -----------------------------
# KNOWLEDGE EXTRACTION
# -----------------------------

def extract_knowledge(transcript):

    prompt = f"""
You are an AI knowledge extraction system.

Extract knowledge from the transcript.

IMPORTANT:
- Return ONLY valid JSON.
- Do NOT use markdown.
- Do NOT use ```json.
- Do NOT add explanations.

Return exactly:

{{
  "problem": "",
  "solution": "",
  "impact": "",
  "context": "",
  "tools": [],
  "reusability": ""
}}

Transcript:
{transcript}
"""

    result = call_llm(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return clean_json_response(result)

# -----------------------------
# SCORING
# -----------------------------

def calculate_innovation_score(extracted_data, similar_cases):

    prompt = f"""
You are an innovation evaluation system.

Evaluate the extracted knowledge.

EXTRACTED KNOWLEDGE:
{json.dumps(extracted_data, indent=2)}

SIMILAR EXISTING CASES:
{json.dumps(similar_cases, indent=2)}

Evaluate:

1. Novelty
- How unique is the idea?
- How different is it from existing approaches?
- Do NOT reduce novelty solely because a related solution exists.

Novelty Guidelines:
1 = Common practice
2 = Small improvement
3 = Moderate improvement
4 = Significant innovation
5 = Highly innovative

2. Impact
- Did the solution create measurable improvement?

3. Reusability
- Can other teams use it?

4. Clarity
- Is it clearly explained?

FINAL SCORE:

final_score =
(0.35 * novelty) +
(0.35 * impact) +
(0.20 * reusability) +
(0.10 * clarity)

Return ONLY JSON.

Example:

{{
  "novelty": 4,
  "impact": 5,
  "reusability": 4,
  "clarity": 5,
  "final_score": 4.5,
  "reasoning": {{
    "novelty": "",
    "impact": "",
    "reusability": "",
    "clarity": ""
  }}
}}
"""

    result = call_llm(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return clean_json_response(result)

# -----------------------------
# INTERVIEW ENDPOINT
# -----------------------------

@app.post("/interview")
def interview(data: InterviewInput):

    system_prompt = """
You are an interviewer collecting innovative work experiences.

Ask ONE question at a time.

Focus on:
- problem
- solution
- tools
- impact
- measurable improvements
- reusability

Keep questions concise and professional.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for msg in data.history:
        messages.append(msg)

    messages.append(
        {
            "role": "user",
            "content": data.user_input
        }
    )

    reply = call_llm(messages)

    return {
        "response": reply
    }

# -----------------------------
# EXTRACT ENDPOINT
# -----------------------------

@app.post("/extract")
def extract(data: TranscriptInput):

    structured = extract_knowledge(
        data.transcript
    )

    return {
        "structured_knowledge": structured
    }

# -----------------------------
# SCORE ENDPOINT
# -----------------------------

@app.post("/score")
def score(data: TranscriptInput):

    extracted = extract_knowledge(
        data.transcript
    )

    similar_cases = retrieve_similar(
        data.transcript
    )

    innovation_score = calculate_innovation_score(
        extracted,
        similar_cases
    )

    return {
        "structured_knowledge": extracted,
        "similar_cases": similar_cases,
        "innovation_score": innovation_score
    }

# -----------------------------
# RUN APP
# -----------------------------

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )