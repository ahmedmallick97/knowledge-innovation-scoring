# AI-based Knowledge Management and Innovation Scoring System

## Project Overview

This project is a prototype Knowledge Management System that uses Large Language Models (LLMs) to capture, structure, and evaluate innovative work experiences.

The system follows three main stages:

1. Interview employees to collect innovative experiences.
2. Extract structured knowledge from the interview transcript.
3. Evaluate the innovation using predefined scoring criteria.

---

## System Workflow

Interview

↓

Knowledge Extraction

↓

Retrieve Similar Cases

↓

Innovation Scoring

---

## Features

- Interview assistant using GPT-5 Mini
- Structured knowledge extraction
- Similar case retrieval using a local dataset
- Innovation scoring
- REST API using FastAPI

---

## Project Structure

```
Knowledge-Innovation-Scoring
│
├── app.py
├── data.json
├── requirements.txt
├── .env.example
├── README.md
│
└── examples
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/ahmedmallick97/knowledge-innovation-scoring.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example`.

Run

```bash
uvicorn app:app --reload
```

Open Swagger

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### POST /interview

Collects interview responses from users.

---

### POST /extract

Extracts structured knowledge:

- Problem
- Solution
- Impact
- Context
- Tools
- Reusability

---

### POST /score

Performs:

- Knowledge Extraction
- Similar Case Retrieval
- Innovation Scoring

---

## Innovation Scoring

The final innovation score is calculated using:

| Criterion | Weight |
|------------|--------|
| Novelty | 35% |
| Impact | 35% |
| Reusability | 20% |
| Clarity | 10% |

Final Score

```
0.35 × Novelty
+ 0.35 × Impact
+ 0.20 × Reusability
+ 0.10 × Clarity
```

---

## Technologies

- Python
- FastAPI
- Azure OpenAI
- GPT-5 Mini
- JSON

---
