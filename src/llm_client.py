# LLM Client wrapper for Ollama API with error handling

import ollama
import json
from src.config import MODEL_NAME, LLM_TIMEOUT, KEEP_ALIVE


class LLMClient:
    """
    Wrapper class for Ollama LLM interactions
    Handles both text generation and JSON generation with fallbacks
    """

    def __init__(self):
        """Initialize LLM client with configuration"""
        self.model = MODEL_NAME
        self.timeout = LLM_TIMEOUT

    def generate_text(self, prompt, system_prompt=""):
        """
        Generate free-form text (for reviews)

        Args:
            prompt: User prompt
            system_prompt: System instructions for the LLM

        Returns:
            str: Generated text
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 150,  # Max tokens
                },
                keep_alive=KEEP_ALIVE  # Keep model in VRAM
            )
            return response['message']['content'].strip()

        except Exception as e:
            print(f"[LLM ERROR - Text Generation] {e}")
            # Fallback response
            return "Product is okay. 3/5 stars."

    def generate_json(self, prompt, system_prompt=""):
        """
        Generate structured JSON (for shopper decisions)

        Args:
            prompt: User prompt
            system_prompt: System instructions for the LLM

        Returns:
            dict: Parsed JSON or default fallback
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                format='json',  # Force JSON output
                options={
                    "temperature": 0.5,  # Lower temp for structured output
                },
                keep_alive=KEEP_ALIVE  # Keep model in VRAM
            )

            content = response['message']['content']
            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"[LLM ERROR - JSON Parse Failed] {e}")
            # Return default decision
            return {
                "decision": "NO_BUY",
                "reasoning": "Unable to evaluate product properly."
            }

        except Exception as e:
            print(f"[LLM ERROR - JSON Generation] {e}")
            return {
                "decision": "NO_BUY",
                "reasoning": "System error occurred."
            }

    def test_connection(self):
        """
        Test if Ollama is accessible and responding

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": "Say OK"}],
                options={"num_predict": 5}
            )
            return True
        except:
            return False
