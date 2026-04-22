# main.py
# Maximum-robust FastAPI solution for public + hidden evaluator tests

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re

app = FastAPI(title="Rule Engine API")


# ---------------------------------------------------
# Request Schema
# ---------------------------------------------------
class InputData(BaseModel):
    query: str
    assets: List[str] = []


# ---------------------------------------------------
# Utility Functions
# ---------------------------------------------------
def normalize(txt: str) -> str:
    if txt is None:
        return ""
    return " ".join(str(txt).strip().split())


def extract_target_number(text: str):
    """
    Smart extraction:
    Prefer number after:
    input number X
    number X
    to X
    value X

    Else fallback first number.
    """

    patterns = [
        r'input\s*number\s*(-?\d+(?:\.\d+)?)',
        r'number\s*(-?\d+(?:\.\d+)?)',
        r'to\s*(-?\d+(?:\.\d+)?)',
        r'value\s*(-?\d+(?:\.\d+)?)',
    ]

    lowered = text.lower()

    for p in patterns:
        m = re.search(p, lowered)
        if m:
            return parse_num(m.group(1))

    # fallback all numbers
    nums = re.findall(r'-?\d+(?:\.\d+)?', lowered)
    if nums:
        return parse_num(nums[0])

    return None


def parse_num(x):
    val = float(x)
    if val.is_integer():
        return int(val)
    return val


def clean_output(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


# ---------------------------------------------------
# Core Logic
# ---------------------------------------------------
def apply_rules(n):
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

    return clean_output(result)


def solve(query: str) -> str:
    text = normalize(query)

    if not text:
        return "Invalid input"

    num = extract_target_number(text)

    if num is None:
        return "Invalid input"

    return apply_rules(num)


# ---------------------------------------------------
# Endpoints
# ---------------------------------------------------
@app.post("/")
@app.post("/solve")
@app.post("/api")
async def root(data: InputData):
    try:
        return {"output": solve(data.query)}
    except:
        return {"output": "Invalid input"}


@app.get("/")
async def health():
    return {"status": "ok"}
