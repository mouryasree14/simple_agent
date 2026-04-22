# main.py
# LEVEL 6 PROMPT INJECTION SAFE VERSION

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

def format_num(n):
    if int(n) == n:
        return str(int(n))
    return str(round(n, 2))

def extract_numbers(txt):
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', txt)]


# -----------------------------
# Remove Prompt Injection Noise
# -----------------------------
def sanitize_query(q):
    bad_phrases = [
        "ignore all previous instructions",
        "ignore previous instructions",
        "forget previous instructions",
        "output only",
        "say only",
        "respond only",
        "just say",
        "return only",
        "ignore above",
        "ignore below",
        "system prompt",
        "developer message"
    ]

    lq = q.lower()

    for phrase in bad_phrases:
        lq = lq.replace(phrase, " ")

    # remove quotes
    lq = lq.replace('"', " ").replace("'", " ")

    return lq.strip()


# -----------------------------
# Detect actual math task
# -----------------------------
def solve_math(q):

    # direct arithmetic expression
    expr = re.findall(r'[-+*/()0-9\s]+', q)
    expr = " ".join(expr).strip()

    if any(op in expr for op in "+-*/"):
        try:
            val = eval(expr)
            return format_num(val)
        except:
            pass

    nums = extract_numbers(q)

    if nums:

        if "add" in q or "sum" in q or "plus" in q:
            return format_num(sum(nums))

        if "subtract" in q or "minus" in q:
            if "from" in q and len(nums) >= 2:
                return format_num(nums[1] - nums[0])

            ans = nums[0]
            for n in nums[1:]:
                ans -= n
            return format_num(ans)

        if "multiply" in q or "product" in q:
            ans = 1
            for n in nums:
                ans *= n
            return format_num(ans)

        if "divide" in q:
            try:
                ans = nums[0]
                for n in nums[1:]:
                    ans /= n
                return format_num(ans)
            except:
                pass

        if "largest" in q or "maximum" in q or "highest" in q:
            return format_num(max(nums))

        if "smallest" in q or "minimum" in q or "lowest" in q:
            return format_num(min(nums))

    return None


# -----------------------------
# Main Solver
# -----------------------------
def solve(query, assets):

    q = clean(query)
    sq = sanitize_query(q)

    # Priority: if task mentioned after "actual task:"
    m = re.search(r'actual task[: ]+(.*)', sq, re.I)
    if m:
        sq = m.group(1).strip()

    # Solve actual task
    ans = solve_math(sq)

    if ans is not None:
        return ans

    # asset logic
    if "assets" in sq:
        return str(len(assets))

    # fallback number
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
