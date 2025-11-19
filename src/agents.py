# Agent classes for Reviewers and Shoppers

from src.llm_client import LLMClient
from src.prompts import (
    GENUINE_REVIEWER_SYSTEM, get_genuine_reviewer_prompt,
    FAKE_REVIEWER_SYSTEM, get_fake_reviewer_prompt,
    SHOPPER_SYSTEM_BASE, get_shopper_prompt
)
from src.database import Review, Transaction
import re


class ReviewerAgent:
    """
    Agent that generates product reviews (genuine or fake)
    """

    def __init__(self, agent_type, personality=None):
        """
        Initialize ReviewerAgent

        Args:
            agent_type: str - 'Genuine' or 'Fake'
            personality: str - 'Critical', 'Balanced', or 'Lenient' (only for Genuine)
        """
        self.agent_type = agent_type
        self.personality = personality
        self.llm = LLMClient()

    def generate_review(self, product, iteration, session):
        """
        Generate and save review to database

        Args:
            product: Product object
            iteration: int - Current simulation iteration
            session: SQLAlchemy session

        Returns:
            Review object
        """
        if self.agent_type == "Genuine":
            return self._generate_genuine(product, iteration, session)
        else:
            return self._generate_fake(product, iteration, session)

    def _generate_genuine(self, product, iteration, session):
        """
        Generate genuine review based on actual product attributes

        Args:
            product: Product object
            iteration: int - Current iteration
            session: SQLAlchemy session

        Returns:
            Review object
        """
        # Prepare product attributes
        attributes = {
            "sound_quality": product.sound_quality,
            "build_quality": product.build_quality,
            "battery_life": product.battery_life,
            "comfort": product.comfort
        }

        # Generate prompt
        prompt = get_genuine_reviewer_prompt(
            product.name, product.price, self.personality, attributes
        )

        # Get LLM response
        response = self.llm.generate_text(prompt, GENUINE_REVIEWER_SYSTEM)

        # Parse response
        rating, text = self._parse_review_response(response)

        # Create Review object
        review = Review(
            product_id=product.id,
            agent_type="Genuine",
            agent_personality=self.personality,
            rating=rating,
            text=text,
            is_fake=False,
            iteration=iteration
        )

        session.add(review)
        session.commit()

        return review

    def _generate_fake(self, product, iteration, session):
        """
        Generate fake positive review with variation

        Args:
            product: Product object
            iteration: int - Current iteration
            session: SQLAlchemy session

        Returns:
            Review object
        """
        # Get varied prompt for fake review
        prompt = get_fake_reviewer_prompt()

        # Get LLM response
        response = self.llm.generate_text(prompt, FAKE_REVIEWER_SYSTEM)

        # Parse response
        rating, text = self._parse_review_response(response)

        # Force 5 stars for fake reviews
        rating = 5

        # Create Review object
        review = Review(
            product_id=product.id,
            agent_type="Fake",
            agent_personality=None,
            rating=rating,
            text=text,
            is_fake=True,
            iteration=iteration
        )

        session.add(review)
        session.commit()

        return review

    def _parse_review_response(self, response):
        """
        Parse LLM response to extract rating and text

        Args:
            response: str - Raw LLM response

        Returns:
            tuple: (rating, text)
        """
        # Try to extract rating with regex
        rating_match = re.search(r'Rating:\s*(\d)', response)
        rating = int(rating_match.group(1)) if rating_match else 3

        # Extract text (everything before "Rating:")
        text_match = re.search(r'Review:\s*(.+?)(?=Rating:|$)', response, re.DOTALL)
        text = text_match.group(1).strip() if text_match else response

        # Clean up
        text = text.replace("Review:", "").strip()

        return rating, text


class ShopperAgent:
    """
    Agent that evaluates products and makes purchase decisions
    """

    def __init__(self, persona):
        """
        Initialize ShopperAgent

        Args:
            persona: str - 'Impulsive', 'Careful', or 'Skeptical'
        """
        self.persona = persona
        self.llm = LLMClient()

    def evaluate_product(self, product, reviews, iteration, session):
        """
        Evaluate product and make purchase decision

        Args:
            product: Product object
            reviews: list of Review objects (NOT dicts) - from ProductManager
            iteration: int - Current iteration
            session: SQLAlchemy session

        Returns:
            Transaction object
        """
        # Convert Review objects to dict format for prompt
        reviews_for_prompt = [
            {
                "text": r.text,
                "rating": r.rating,
                "iteration": r.iteration
            }
            for r in reviews
        ]

        # Generate prompt
        prompt = get_shopper_prompt(
            product.name,
            product.price,
            product.current_rating,
            reviews_for_prompt,
            self.persona
        )

        # Get decision from LLM (JSON format)
        decision_json = self.llm.generate_json(prompt, SHOPPER_SYSTEM_BASE)

        # Count fake reviews in sample (NO DATABASE QUERY - direct attribute access)
        fake_count = sum(1 for r in reviews if r.is_fake)

        # Create Transaction
        transaction = Transaction(
            product_id=product.id,
            buyer_persona=self.persona,
            decision=decision_json.get("decision", "NO_BUY"),
            reasoning=decision_json.get("reasoning", "No reasoning provided"),
            reviews_read=len(reviews),
            fake_in_sample=fake_count,
            iteration=iteration
        )

        session.add(transaction)
        session.commit()

        return transaction
