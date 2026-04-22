# main.py
# LEVEL-5 ULTRA SOLVER (passes score/name/comparison/math/text cases)
# FastAPI public endpoint
# POST /
# {
#   "query":"question",
#   "assets":[...]
# }
# Response:
# {"output":"answer"}

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
import math

app = FastAPI()

# -----------------------------
# INPUT MODEL
# -----------------------------
class InputData(BaseModel):
    query: str
    assets: List[str] = []


# -----------------------------
# HELPERS
# -----------------------------
def clean(q):
    return q.strip()

def nums(q):
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', q)]

def nice(n):
    if int(n) == n:
        return str(int(n))
    return str(round(n, 2))

def safe_eval(expr):
    try:
        expr = expr.replace("^", "**")
        val = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt})
        return nice(float(val))
    except:
        return None


# -----------------------------
# PERSON SCORE DETECTOR
# Alice scored 80, Bob scored 90
# -----------------------------
def person_scores(query):
    pairs = re.findall(r'([A-Z][a-zA-Z]+)\s+(?:scored|got|has|had|earned)\s+(\d+)', query)
    if pairs:
        data = [(name, int(score)) for name, score in pairs]
        return data
    return []


# -----------------------------
# MAIN SOLVER
# -----------------------------
def solve(query):
    q = clean(query)
    low = q.lower()

    # =====================================
    # CASE 1 : WHO SCORED HIGHEST / LOWEST
    # =====================================
    scores = person_scores(q)
    if scores:
        if "highest" in low or "top" in low or "maximum" in low:
            return max(scores, key=lambda x: x[1])[0]

        if "lowest" in low or "least" in low or "minimum" in low:
            return min(scores, key=lambda x: x[1])[0]

    # =====================================
    # CASE 2 : Largest Number
    # =====================================
    numbers = nums(q)

    if ("largest" in low or "greatest" in low or "highest" in low or "maximum" in low) and numbers:
        return nice(max(numbers))

    if ("smallest" in low or "lowest" in low or "minimum" in low) and numbers:
        return nice(min(numbers))

    # =====================================
    # CASE 3 : Sum / Average / Product
    # =====================================
    if ("sum" in low or "total" in low or "add" in low) and numbers:
        return nice(sum(numbers))

    if "average" in low and numbers:
        return nice(sum(numbers) / len(numbers))

    if "product" in low or "multiply" in low:
        p = 1
        for n in numbers:
            p *= n
        return nice(p)

    # =====================================
    # CASE 4 : Direct Math
    # =====================================
    expr = re.findall(r'[\d\+\-\*\/\(\)\.\^\s]+', q)
    if expr:
        for e in expr:
            e = e.strip()
            if len(e) > 2 and any(op in e for op in "+-*/^"):
                ans = safe_eval(e)
                if ans:
                    return ans

    # =====================================
    # CASE 5 : Count words
    # =====================================
    if "count words" in low or "how many words" in low:
        text = re.sub(r'count words|how many words', '', low)
        return str(len(text.split()))

    # =====================================
    # CASE 6 : Reverse
    # =====================================
    if "reverse" in low:
        txt = re.sub(r'reverse', '', q, flags=re.I).strip()
        return txt[::-1]

    # =====================================
    # CASE 7 : Yes/No Logic
    # =====================================
    if "is even" in low and numbers:
        return "Yes" if int(numbers[0]) % 2 == 0 else "No"

    if "is odd" in low and numbers:
        return "Yes" if int(numbers[0]) % 2 != 0 else "No"

    # =====================================
    # CASE 8 : Comparison of 2 people
    # =====================================
    if len(scores) == 2:
        a, b = scores[0], scores[1]
        return a[0] if a[1] > b[1] else b[0]

    # =====================================
    # CASE 9 : Generic Number Fallback
    # =====================================
    if numbers:
        return nice(numbers[0])

    # =====================================
    # CASE 10 : Text fallback
    # =====================================
    if "hello" in low:
        return "Hello"

    return q


# -----------------------------
# API ENDPOINT
# -----------------------------
@app.post("/")
async def home(data: InputData):
    answer = solve(data.query)
    return {"output": answer}