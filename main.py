# main.py
# LEVEL 6 PERFECT SCORE - PROMPT INJECTION SAFE

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
import math

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
# Prompt Injection Cleaner
# -----------------------------
def sanitize_query(txt):
    bad_words = [
        "ignore all previous instructions",
        "ignore previous instructions",
        "forget previous instructions",
        "output only",
        "say only",
        "respond only",
        "return only",
        "just output",
        "just say",
        "developer prompt",
        "system prompt"
    ]

    t = lower(txt)

    for w in bad_words:
        t = t.replace(w, " ")

    t = t.replace('"', " ").replace("'", " ")
    return t.strip()


# -----------------------------
# Solve Arithmetic
# -----------------------------
def solve_math(txt):

    # Priority: Actual Task
    m = re.search(r'actual task[: ]+(.*)', txt, re.I)
    if m:
        txt = m.group(1).strip()

    nums = extract_numbers(txt)

    # Direct expression
    expr = re.sub(r'[^0-9+\-*/(). ]', '', txt)

    if any(op in expr for op in "+-*/"):
        try:
            val = eval(expr)
            return format_num(val)
        except:
            pass

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

        if any(x in txt for x in ["largest", "highest", "maximum", "max"]):
            return format_num(max(nums))

        if any(x in txt for x in ["smallest", "lowest", "minimum", "min"]):
            return format_num(min(nums))

        if "average" in txt or "mean" in txt:
            return format_num(sum(nums) / len(nums))

    return None


# -----------------------------
# Main Solver
# -----------------------------
def solve(query, assets):

    q = clean(query)
    sq = sanitize_query(q)

    # Solve math / actual task
    ans = solve_math(sq)
    if ans is not None:
        return ans

    # Assets logic
    if "assets" in sq:
        return str(len(assets))

    # Word count
    if "count words" in sq or "how many words" in sq:
        t = re.sub(r'count words|how many words', '', sq).strip()
        return str(len(t.split()))

    # Reverse
    if "reverse" in sq:
        t = re.sub(r'reverse', '', sq).strip()
        return t[::-1]

    # Greeting
    if any(x in sq for x in ["hello", "hi", "hey"]):
        return "Hello"

    # Fallback
    nums = extract_numbers(sq)
    if nums:
        return format_num(nums[0])

    return "I cannot solve this."


# -----------------------------
# API
# -----------------------------
@app.post("/")
async def root(data: InputData):
    ans = solve(data.query, data.assets)
    return {"output": ans}
