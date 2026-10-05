import os
import traceback
from typing import Dict
import dspy
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Prompt Template
INSIGHT_PROMPT_TEMPLATE = """
You are a helpful financial analyst. Given the ticker {ticker} and the following data,
produce a concise investment analysis (3–6 short paragraphs) covering:
- recent price action summary
- key fundamental metrics (PE, beta)
- risk considerations
- investment thesis and recommended time horizon

Raw data:
{raw_summary}
"""

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_DSPY = False

# Initialize DSPy model
try:
    lm = dspy.LM(model="openai/gpt-4", api_key=OPENAI_API_KEY)
    dspy.configure(lm=lm)
    USE_DSPY = True
except Exception:
    USE_DSPY = False

# Initialize OpenAI client (fallback option)
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception:
    client = None

# ---------------------------------------------------------------------
#  Task 4: Implement Financial Insight Generation using DSPy
# ---------------------------------------------------------------------

