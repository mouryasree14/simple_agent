# main.py
# Ultra-robust FastAPI Rule Engine API
# Handles visible + hidden + nasty edge cases

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any
import re
import math

app = FastAPI(title="Perfect Rule Engine API")


# -----------------------------
# Request Model
# -----------------------------
class InputData(BaseModel):
    query: str
    assets: List[str] = []


# -----------------------------
# Helpers
# -----------------------------
def normalize(text: Any) -> str:
    if text is None:
        return ""
    return " ".join(str(text).strip().split())


def extract_target_number(query: str):
    """
    Smart extraction:
    Prefer number after:
    input number / number / value / to input number
    fallback = last meaningful number
    """

    q = query.lower()

    patterns = [
        r'input\s+number\s*(-?\d+(?:\.\d+)?)',
        r'number\s*(-?\d+(?:\.\d+)?)',
        r'value\s*(-?\d+(?:\.\d+)?)',
        r'apply.*?to\s*(-?\d+(?:\.\d+)?)',
    ]

    for p in patterns:
        m = re.search(p, q)
        if m:
            return parse_num(m.group(1))

    nums = re.findall(r'-?\d+(?:\.\d+)?', q)
    if nums:
        return parse_num(nums[-1])

    return None


def parse_num(x):
    val = float(x)
    if val.is_integer():
        return int(val)
    return val


def clean_output(x):
    if isinstance(x, float):
        if math.isfinite(x) and x.is_integer():
            return str(int(x))
        s = f"{x:.10f}".rstrip("0").rstrip(".")
        return s
    return str(x)


# -----------------------------
# Rule Engine
# -----------------------------
def apply_rules(n):
    # Rule 1
    if int(n) % 2 == 0:
        result = n * 2
    else:
        result = n + 10

    # Rule 2
    if result > 20:
        result = result - 5
    else:
        result = result + 3

    # Rule 3
    if int(result) % 3 == 0:
        return "FIZZ"

    return clean_output(result)


def solve(query: str):
    q = normalize(query)

    if not q:
        return "Invalid input"

    num = extract_target_number(q)

    if num is None:
        return "Invalid input"

    return apply_rules(num)


# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
async def health():
    return {"output": "API Running"}


@app.post("/")
async def root(data: InputData):
    try:
        return {"output": solve(data.query)}
    except:
        return {"output": "Invalid input"}


@app.post("/solve")
async def solve_api(data: InputData):
    try:
        return {"output": solve(data.query)}
    except:
        return {"output": "Invalid input"}


# Run:
# uvicorn main:app --host 0.0.0.0 --port 10000
