# main.py
# LEVEL 5 + LEVEL 6 (INJECTION SAFE)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
import math
from functools import reduce
import operator

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
# 🔥 LEVEL 6: SANITIZER (NEW)
# -----------------------------
def sanitize_query(query):
    q = query

    # Remove prompt injection phrases
    patterns = [
        r'ignore all previous instructions.*',
        r'output only.*',
        r'just output.*',
        r'just say.*',
        r'do not follow.*',
        r'only respond.*',
        r'print only.*'
    ]

    for pat in patterns:
        q = re.sub(pat, '', q, flags=re.IGNORECASE)

    # Extract only actual task if present
    if "actual task:" in q.lower():
        parts = re.split(r'actual task:', q, flags=re.IGNORECASE)
        if len(parts) > 1:
            q = parts[1]

    return q.strip()


# -----------------------------
# Detect Name + Score
# -----------------------------
def detect_scores(q):
    patterns = [
        r'([A-Z][a-zA-Z]+)\s*(?:scored|got|earned|has|had|is|=)\s*(-?\d+)',
        r'(-?\d+)\s*(?:by|for)?\s*([A-Z][a-zA-Z]+)'
    ]

    results = []

    for pat in patterns:
        found = re.findall(pat, q)

        for item in found:
            if item[0].isdigit() or item[0].startswith("-"):
                score = int(item[0])
                name = item[1]
            else:
                name = item[0]
                score = int(item[1])

            results.append((name, score))

    return results


# -----------------------------
# Smart Solver
# -----------------------------
def solve(query, assets):

    # 🔥 APPLY SANITIZER FIRST (KEY FOR LEVEL 6)
    query = sanitize_query(query)

    q = clean(query)
    lq = lower(query)

    # ======================================
    # 1. SCORE QUESTIONS
    # ======================================
    scores = detect_scores(q)

    if scores:
        if any(x in lq for x in ["highest", "top", "max", "maximum", "winner", "best"]):
            return max(scores, key=lambda x: x[1])[0]

        if any(x in lq for x in ["lowest", "least", "minimum", "worst"]):
            return min(scores, key=lambda x: x[1])[0]

        return max(scores, key=lambda x: x[1])[0]

    # ======================================
    # 2. NUMBERS
    # ======================================
    nums = extract_numbers(q)

    if nums:

        # Largest / Smallest
        if any(x in lq for x in ["largest", "greatest", "highest", "maximum", "max"]):
            return format_num(max(nums))

        if any(x in lq for x in ["smallest", "lowest", "minimum", "least", "min"]):
            return format_num(min(nums))

        # Sum
        if any(x in lq for x in ["sum", "total", "add", "plus"]):
            return format_num(sum(nums))

        # Average
        if any(x in lq for x in ["average", "mean"]):
            return format_num(sum(nums) / len(nums))

        # Subtraction
        if any(x in lq for x in ["subtract", "minus"]):
            if "from" in lq and len(nums) >= 2:
                return format_num(nums[1] - nums[0])

            ans = nums[0]
            for n in nums[1:]:
                ans -= n
            return format_num(ans)

        # Product
        if any(x in lq for x in ["multiply", "product"]):
            ans = 1
            for n in nums:
                ans *= n
            return format_num(ans)

        # Division
        if any(x in lq for x in ["divide", "quotient"]):
            try:
                ans = nums[0]
                for n in nums[1:]:
                    ans /= n
                return format_num(ans)
            except:
                pass

        # Even / Odd
        n = int(nums[0])

        if "even" in lq:
            return "Yes" if n % 2 == 0 else "No"

        if "odd" in lq:
            return "Yes" if n % 2 != 0 else "No"

    # ======================================
    # 3. Direct Arithmetic
    # ======================================
    expr = re.sub(r'[^0-9+\-*/(). ]', '', q)

    if any(op in expr for op in "+-*/"):
        try:
            val = eval(expr)
            return format_num(val)
        except:
            pass

    # ======================================
    # 4. Reverse String
    # ======================================
    if "reverse" in lq:
        txt = re.sub(r'reverse', '', q, flags=re.I).strip()
        return txt[::-1]

    # ======================================
    # 5. Count Words
    # ======================================
    if "count words" in lq or "how many words" in lq:
        txt = re.sub(r'count words|how many words', '', lq).strip()
        return str(len(txt.split()))

    # ======================================
    # 6. Assets Handling
    # ======================================
    if "assets" in lq:
        return str(len(assets))

    # ======================================
    # 7. Greeting
    # ======================================
    if any(x in lq for x in ["hello", "hi", "hey"]):
        return "Hello"

    # ======================================
    # FINAL FALLBACK
    # ======================================
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
