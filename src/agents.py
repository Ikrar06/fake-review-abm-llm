# agents.py - MESA Agents for Fake Review Simulation

from mesa import Agent
from src.llm_client import LLMClient
from src.prompts import (
    GENUINE_REVIEWER_SYSTEM, get_genuine_reviewer_prompt,
    FAKE_REVIEWER_SYSTEM, get_fake_reviewer_prompt,
    SHOPPER_SYSTEM_BASE, get_shopper_prompt
)
import re
from typing import Dict, Tuple, List


class ReviewerAgent(Agent):
    """Agent that generates product reviews (genuine or fake)."""

    def __init__(self, unique_id, model, agent_type: str, personality: str = None):
        super().__init__(unique_id, model)
        self.agent_type = agent_type
        self.personality = personality
        self.llm = LLMClient()

    def generate_review(self, product, iteration: int) -> Dict:
        if self.agent_type == "Genuine":
            return self._generate_genuine(product, iteration)
        return self._generate_fake(product, iteration)

    def _generate_genuine(self, product, iteration: int) -> Dict:
        attributes = {
            "sound_quality": product.sound_quality,
            "build_quality": product.build_quality,
            "battery_life": product.battery_life,
            "comfort": product.comfort
        }

        prompt = get_genuine_reviewer_prompt(
            product.name, product.price, self.personality, attributes
        )
        response = self.llm.generate_text(prompt, GENUINE_REVIEWER_SYSTEM)
        rating, text = self._parse_review_response(response)

        return {"rating": rating, "text": text}

    def _generate_fake(self, product, iteration: int) -> Dict:
        prompt = get_fake_reviewer_prompt()
        response = self.llm.generate_text(prompt, FAKE_REVIEWER_SYSTEM)
        rating, text = self._parse_review_response(response)
        rating = 5  # Force 5 stars

        return {"rating": rating, "text": text}

    def _parse_review_response(self, response: str) -> Tuple[int, str]:
        rating_match = re.search(r'Rating:\s*(\d)', response)
        rating = int(rating_match.group(1)) if rating_match else 3
        rating = max(1, min(5, rating))

        text_match = re.search(r'Review:\s*(.+?)(?=Rating:|$)', response, re.DOTALL)
        text = text_match.group(1).strip() if text_match else response
        text = text.replace("Review:", "").strip()

        if not text:
            text = "No review text provided"

        return rating, text

    def step(self):
        pass


class ShopperAgent(Agent):
    """Agent that evaluates products and makes purchase decisions."""

    def __init__(self, unique_id, model, persona: str):
        super().__init__(unique_id, model)
        self.persona = persona
        self.llm = LLMClient()
        self.decision = None
        self.reasoning = None

    def evaluate_product(self, product, reviews: List[Dict], iteration: int) -> Tuple[str, str]:
        reviews_for_prompt = [
            {"text": r['text'], "rating": r['rating'], "iteration": r['iteration']}
            for r in reviews
        ]

        prompt = get_shopper_prompt(
            product.name, product.price, product.current_rating,
            reviews_for_prompt, self.persona, iteration=iteration
        )

        decision_json = self.llm.generate_json(prompt, SHOPPER_SYSTEM_BASE)
        self.decision = decision_json.get("decision", "NO_BUY")
        self.reasoning = decision_json.get("reasoning", "No reasoning provided")

        return self.decision, self.reasoning

    def step(self):
        pass
