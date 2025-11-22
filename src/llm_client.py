# llm_client.py - Ollama LLM Client

import ollama
import json
import time
from typing import Dict, Tuple
from src.config import MODEL_NAME, LLM_TIMEOUT, KEEP_ALIVE


class LLMClient:
    """LLM client with dynamic context window and automatic retry."""

    def __init__(self, verbose: bool = False):
        self.model = MODEL_NAME
        self.timeout = LLM_TIMEOUT
        self.verbose = verbose
        self.DEFAULT_CONTEXT = 2048
        self.LARGE_CONTEXT = 4096
        self.MAX_CONTEXT = 8192

        if self.verbose:
            print(f"[LLM] Initialized with model: {self.model}")

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def _get_optimal_context_size(self, prompt: str, system_prompt: str) -> int:
        total_text = system_prompt + prompt
        estimated_tokens = self._estimate_tokens(total_text)
        estimated_with_buffer = estimated_tokens + 350

        if estimated_with_buffer <= self.DEFAULT_CONTEXT:
            return self.DEFAULT_CONTEXT
        elif estimated_with_buffer <= self.LARGE_CONTEXT:
            return self.LARGE_CONTEXT
        return self.MAX_CONTEXT

    def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        max_retries: int = 3,
        temperature: float = 0.6,
        max_tokens: int = 300,
    ) -> str:
        """Generate free-form text (for reviews)."""
        context_size = self._get_optimal_context_size(prompt, system_prompt)

        for attempt in range(max_retries):
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    options={
                        "num_ctx": context_size,
                        "num_predict": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                    },
                    keep_alive=KEEP_ALIVE
                )

                content = response['message']['content'].strip()
                if not content or len(content) < 10:
                    raise ValueError("Generated content too short")
                return content

            except Exception as e:
                error_msg = str(e)
                if "context" in error_msg.lower() or "length" in error_msg.lower():
                    if context_size < self.MAX_CONTEXT:
                        context_size = self.MAX_CONTEXT
                    else:
                        return self._generate_fallback_review()

                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return self._generate_fallback_review()

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        max_retries: int = 3,
        temperature: float = 0.3,
    ) -> Dict:
        """Generate structured JSON (for shopper decisions)."""
        context_size = self._get_optimal_context_size(prompt, system_prompt)

        for attempt in range(max_retries):
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    format='json',
                    options={
                        "num_ctx": context_size,
                        "num_predict": 250,
                        "temperature": temperature,
                        "top_p": 0.9,
                    },
                    keep_alive=KEEP_ALIVE
                )

                content = response['message']['content'].strip()
                parsed = json.loads(content)
                return self._validate_decision_json(parsed)

            except json.JSONDecodeError:
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    return self._generate_fallback_decision()

            except Exception as e:
                error_msg = str(e)
                if "context" in error_msg.lower() or "length" in error_msg.lower():
                    if context_size < self.MAX_CONTEXT:
                        context_size = self.MAX_CONTEXT
                    else:
                        return self._generate_fallback_decision()

                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return self._generate_fallback_decision()

    def _validate_decision_json(self, data: Dict) -> Dict:
        if "decision" not in data:
            data["decision"] = "NO_BUY"
        if "reasoning" not in data:
            data["reasoning"] = "No reasoning provided"

        decision_upper = str(data["decision"]).upper()
        if decision_upper not in ["BUY", "NO_BUY"]:
            reasoning_lower = data.get("reasoning", "").lower()
            if any(word in reasoning_lower for word in ["buy", "purchase", "worth"]):
                data["decision"] = "BUY"
            else:
                data["decision"] = "NO_BUY"
        else:
            data["decision"] = decision_upper

        return data

    def _generate_fallback_review(self) -> str:
        return "Review: Product has acceptable quality for the price.\nRating: 3"

    def _generate_fallback_decision(self) -> Dict:
        return {"decision": "NO_BUY", "reasoning": "Unable to evaluate product."}

    def test_connection(self) -> Tuple[bool, str]:
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": "Respond with OK"}],
                options={"num_predict": 10}
            )
            content = response['message']['content'].strip()
            if content:
                return True, f"Connected to '{self.model}'"
            return False, f"Model '{self.model}' returned empty response"
        except Exception as e:
            return False, f"Connection failed: {e}"
