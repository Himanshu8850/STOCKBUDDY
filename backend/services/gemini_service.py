import os
import json
import re
import requests
import time
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
    
    def _parse_gemini_text_to_json(self, text: str):
        """Best-effort parser to extract JSON from Gemini text responses."""
        cleaned = re.sub(r"```(?:json|JSON)?", "", text)
        cleaned = cleaned.replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and end > start:
                snippet = cleaned[start:end + 1]
                try:
                    return json.loads(snippet)
                except Exception:
                    return None
            return None
    
    def get_prediction(self, stock):
        """Get Gemini AI prediction for a single stock."""
        prompt = f"""
        You are an equities analyst focused on swing trading (1-4 weeks horizon).
        Analyze the following stock and provide:
        - 2 pros (swing-trade relevant: momentum, catalysts, support/resistance, volume, risk/reward)
        - 2 cons (risks: earnings/catalyst risk, volatility, overhead supply, macro headwinds)
        - A verdict: strictly one of "Swing Buy", "Neutral", or "Avoid" followed by a brief reason in the same string
        Stock: {stock}
        Return ONLY valid JSON with keys exactly: pros (array of strings), cons (array of strings), verdict (string). No markdown, no code fences, no extra text.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}],
            }]
        }
        
        try:
            if not self.api_key:
                return {"pros": [], "cons": [], "verdict": "AI error: Missing GEMINI_API_KEY/GOOGLE_API_KEY env"}

            response = requests.post(self.api_url, headers=headers, json=data, timeout=40)
            if response.ok:
                result = response.json()
                try:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    text = json.dumps(result)

                parsed = self._parse_gemini_text_to_json(text)
                if isinstance(parsed, dict):
                    pros = parsed.get('pros') if isinstance(parsed.get('pros'), list) else []
                    cons = parsed.get('cons') if isinstance(parsed.get('cons'), list) else []
                    verdict = parsed.get('verdict') if isinstance(parsed.get('verdict'), str) else ""
                    return {"pros": pros, "cons": cons, "verdict": verdict or ""}

                return {"pros": [], "cons": [], "verdict": text.strip()}
            else:
                logger.error(f"Gemini API error {response.status_code}: {response.text[:500]}")
                return {"pros": [], "cons": [], "verdict": f"AI error: {response.status_code}"}
        except Exception as e:
            logger.exception("Gemini API call failed")
            return {"pros": [], "cons": [], "verdict": f"Error: {e}"}
    
    def get_predictions_batch(self, stocks_batch):
        """Get Gemini AI predictions for multiple stocks in one request."""
        stocks_csv = ", ".join(stocks_batch)
        prompt = f"""
        You are an equities analyst focused on swing trading (1-4 weeks horizon).
        For EACH of the following stocks: {stocks_csv}
        provide:
        - 2 pros (swing-trade relevant: momentum, catalysts, S/R, volume, risk/reward)
        - 2 cons (risks: earnings/catalyst risk, volatility, overhead supply, macro)
        - A verdict: strictly one of "Swing Buy", "Neutral", or "Avoid" followed by a brief reason in the same string
        Return ONLY a single JSON object mapping each stock symbol to an object with keys pros (array), cons (array), verdict (string). No markdown, no code fences, no extra text.
        Example format only:
        {{
          "TCS": {{"pros": ["..."], "cons": ["..."], "verdict": "Swing Buy - reason"}},
          "INFY": {{"pros": ["..."], "cons": ["..."], "verdict": "Neutral - reason"}}
        }}
        """
        
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}

        if not self.api_key:
            return {sym: {"pros": [], "cons": [], "verdict": "AI error: Missing GEMINI_API_KEY/GOOGLE_API_KEY env"} for sym in stocks_batch}

        max_retries = 3
        backoff_seconds = 1
        last_status_code = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=data, timeout=70)
                if response.ok:
                    result = response.json()
                    try:
                        text = result["candidates"][0]["content"]["parts"][0]["text"]
                    except Exception:
                        text = json.dumps(result)
                    
                    parsed = self._parse_gemini_text_to_json(text)
                    if isinstance(parsed, dict):
                        normalized = {}
                        for sym in stocks_batch:
                            payload = parsed.get(sym) or parsed.get(sym.upper()) or parsed.get(sym.lower())
                            if isinstance(payload, dict):
                                pros = payload.get('pros') if isinstance(payload.get('pros'), list) else []
                                cons = payload.get('cons') if isinstance(payload.get('cons'), list) else []
                                verdict = payload.get('verdict') if isinstance(payload.get('verdict'), str) else ""
                                normalized[sym] = {"pros": pros, "cons": cons, "verdict": verdict}
                            else:
                                normalized[sym] = {"pros": [], "cons": [], "verdict": "AI error: malformed batch item"}
                        return normalized
                    
                    return {sym: {"pros": [], "cons": [], "verdict": "AI error: invalid response"} for sym in stocks_batch}
                else:
                    last_status_code = response.status_code
                    logger.error(f"Gemini API error {response.status_code}: {response.text[:500]}")
                    if response.status_code == 503 and attempt < max_retries - 1:
                        time.sleep(backoff_seconds)
                        backoff_seconds *= 2
                        continue
                    break
            except Exception as e:
                logger.exception("Gemini batch call failed")
                if attempt < max_retries - 1:
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                    continue
                last_status_code = 500
                break
        
        # Fallback: call per-symbol
        fallback_results = {}
        for sym in stocks_batch:
            fallback_results[sym] = self.get_prediction(sym)
            time.sleep(0.4)
        
        if all((r.get('verdict','').lower().startswith('ai error') or r.get('verdict','').lower().startswith('error')) for r in fallback_results.values()):
            code = last_status_code or 'unknown'
            return {sym: {"pros": [], "cons": [], "verdict": f"AI error: {code}"} for sym in stocks_batch}
        return fallback_results