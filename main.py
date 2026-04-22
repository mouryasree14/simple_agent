# main.py
# FINAL PERFECT SCORE VERSION

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()


# -----------------------------
# Request Model
# -----------------------------
class InputData(BaseModel):
    query: str
    assets: List[str] = []


# -----------------------------
# Utilities
# -----------------------------
def clean(txt):
    return txt.strip()


def lower(txt):
    return txt.lower().strip()


def extract_numbers(txt):
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', txt)]


def format_num(n):
    if int(n) == n:
        return str(int(n))
    return str(round(n, 2))


# -----------------------------
# Remove Prompt Injection
# -----------------------------
def sanitize_query(txt):
    txt = lower(txt)

    bad_words = [
        "ignore all previous instructions",
        "ignore previous instructions",
        "forget previous instructions",
        "output only",
        "respond only",
        "say only",
        "return only",
        "just output",
        "just say",
        "developer prompt",
        "system prompt"
    ]

    for word in bad_words:
        txt = txt.replace(word, " ")

    txt = txt.replace('"', ' ').replace("'", " ")
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt


# -----------------------------
# Extract Actual Task
# -----------------------------
def extract_task(txt):
    match = re.search(r'actual task\s*:\s*(.*)', txt, re.I)
    if match:
        return match.group(1).strip()
    return txt


# -----------------------------
# Safe Math Solver
# -----------------------------
def solve_math(txt):
    txt = extract_task(txt)

    # direct arithmetic
    expr = re.sub(r'[^0-9+\-*/(). ]', '', txt)

    if any(op in expr for op in ['+', '-', '*', '/']):
        try:
            value = eval(expr, {"__builtins__": None}, {})
            return format_num(value)
        except:
            pass

    nums = extract_numbers(txt)

    if nums:
        if any(x in txt for x in ["add", "sum", "plus"]):
            return format_num(sum(nums))

        if any(x in txt for x in ["subtract", "minus"]):
            if "from" in txt and len(nums) >= 2:
                return format_num(nums[1] - nums[0])

            ans = nums[0]
            for n in nums[1:]:
                ans -= n
            return format_num(ans)

        if any(x in txt for x in ["multiply", "product"]):
            ans = 1
            for n in nums:
                ans *= n
            return format_num(ans)

        if "divide" in txt:
            try:
                ans = nums[0]
                for n in nums[1:]:
                    ans /= n
                return format_num(ans)
            except:
                pass

        if "average" in txt or "mean" in txt:
            return format_num(sum(nums) / len(nums))

        if any(x in txt for x in ["largest", "maximum", "max"]):
            return format_num(max(nums))

        if any(x in txt for x in ["smallest", "minimum", "min"]):
            return format_num(min(nums))

    return None


# -----------------------------
# Main Solver
# -----------------------------
def solve(query, assets):
    q = clean(query)
    sq = sanitize_query(q)

    # Priority 1 → solve actual task
    ans = solve_math(sq)
    if ans is not None:
        return ans

    # Assets count
    if "assets" in sq:
        return str(len(assets))

    # Word count
    if "count words" in sq or "how many words" in sq:
        txt = re.sub(r'count words|how many words', '', sq).strip()
        return str(len(txt.split()))

    # Reverse
    if "reverse" in sq:
        txt = re.sub(r'reverse', '', sq).strip()
        return txt[::-1]

    # Greeting
    if any(x in sq for x in ["hello", "hi", "hey"]):
        return "Hello"

    # Fallback first number
    nums = extract_numbers(sq)
    if nums:
        return format_num(nums[0])

    return "I cannot solve this."


# -----------------------------
# API
# -----------------------------
@app.post("/")
async def root(data: InputData):
    answer = solve(data.query, data.assets)
    return {"output": answer}
