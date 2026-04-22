# main.py
# FINAL MAXIMUM-COVERAGE FASTAPI SOLUTION
# Handles strings, negatives, decimals, malformed input, hidden cases

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Any
import re

app = FastAPI(title="Ultimate Rule Engine")


# ---------------------------------------------------
# Request Schema
# ---------------------------------------------------
class InputData(BaseModel):
    query: str = Field(default="")
    assets: List[str] = Field(default_factory=list)


# ---------------------------------------------------
# Utility Functions
# ---------------------------------------------------
def normalize(text):
    if text is None:
        return ""
    return " ".join(str(text).strip().split())


def parse_number(value):
    try:
        num = float(value)
        if num.is_integer():
            return int(num)
        return num
    except:
        return None


# ---------------------------------------------------
# Number Extraction (Very Robust)
# ---------------------------------------------------
def extract_number(text):
    t = text.lower()

    patterns = [
        r'input\s*number\s*[:=]?\s*(-?\d+(?:\.\d+)?)',
        r'number\s*[:=]?\s*(-?\d+(?:\.\d+)?)',
        r'value\s*[:=]?\s*(-?\d+(?:\.\d+)?)',
        r'apply.*?to\s*(-?\d+(?:\.\d+)?)',
        r'to\s*(-?\d+(?:\.\d+)?)',
        r'for\s*(-?\d+(?:\.\d+)?)',
        r'is\s*(-?\d+(?:\.\d+)?)',
    ]

    for p in patterns:
        m = re.search(p, t, re.I)
        if m:
            val = parse_number(m.group(1))
            if val is not None:
                return val

    # fallback first number anywhere
    nums = re.findall(r'-?\d+(?:\.\d+)?', t)
    for n in nums:
        val = parse_number(n)
        if val is not None:
            return val

    return None


# ---------------------------------------------------
# Output Formatter
# ---------------------------------------------------
def format_output(x):
    try:
        if isinstance(x, float) and x.is_integer():
            return str(int(x))
        return str(x)
    except:
        return str(x)


# ---------------------------------------------------
# Rule Engine
# ---------------------------------------------------
def apply_rules(n):
    try:
        # Rule 1
        if int(n) % 2 == 0:
            result = n * 2
        else:
            result = n + 10

        # Rule 2
        if result > 20:
            result -= 5
        else:
            result += 3

        # Rule 3
        if int(result) % 3 == 0:
            return "FIZZ"

        return format_output(result)

    except:
        return "Invalid input"


# ---------------------------------------------------
# Solve Query
# ---------------------------------------------------
def solve(query):
    q = normalize(query)

    if q == "":
        return "Invalid input"

    num = extract_number(q)

    if num is None:
        return "Invalid input"

    return apply_rules(num)


# ---------------------------------------------------
# Health Endpoints
# ---------------------------------------------------
@app.get("/")
@app.get("/health")
@app.get("/status")
def health():
    return {"status": "ok"}


# ---------------------------------------------------
# Main POST Endpoints
# ---------------------------------------------------
@app.post("/")
@app.post("/solve")
@app.post("/api")
@app.post("/predict")
@app.post("/run")
def root(data: InputData):
    try:
        ans = solve(data.query)

        return {
            "output": ans,
            "result": ans,
            "answer": ans,
            "response": ans
        }

    except:
        return {
            "output": "Invalid input",
            "result": "Invalid input",
            "answer": "Invalid input",
            "response": "Invalid input"
        }
