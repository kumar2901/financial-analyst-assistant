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

def dsp_financial_insight(ticker: str, stock_data: Dict) -> str:
    try:
        raw_data = {
            "company": stock_data.get("company"),
            "sector": stock_data.get("sector"),
            "price": stock_data.get("price"),
            "change_pct": stock_data.get("change_pct"),
            "pe_ratio": stock_data.get("pe_ratio"),
            "beta": stock_data.get("beta"),
        }
        raw_summary = "\n".join([f"{k}: {v}" for k, v in raw_data.items()])
        prompt = INSIGHT_PROMPT_TEMPLATE.format(ticker=ticker, raw_summary=raw_summary)
        # Option 1: DSPy-based Analysis (Preferred)
        if USE_DSPY:
            try:
                predictor = dspy.Predict("input_text -> analysis_text", llm=lm)
                result = predictor(input_text=prompt)
                return getattr(result, "analysis_text", str(result))
            except Exception:
                traceback.print_exc()
        # Option 2: OpenAI Fallback
        if client and OPENAI_API_KEY:
            try:
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=[
                        {"role": "system", "content": "You are a helpful financial analyst."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_tokens=700,
                )
                return response.choices[0].message.content.strip()
            except Exception:
                traceback.print_exc()
        # Option 3: Heuristic Fallback (No AI available)
        heuristic_text = (
            f"Analysis for {ticker}:\n"
            f"Price: {stock_data.get('price')}\n"
            f"P/E Ratio: {stock_data.get('pe_ratio')}\n"
            f"Beta: {stock_data.get('beta')}\n\n"
            f"(Insight generation service unavailable. "
            f"Please verify your OPENAI_API_KEY and DSPy setup.)"
        )
        return heuristic_text
    except Exception as e:
        traceback.print_exc()
        return f"Failed to generate insight: {e}"
