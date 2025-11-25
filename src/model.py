# model.py - MESA Simulation Model

from mesa import Model
from mesa.datacollection import DataCollector
from dataclasses import dataclass, field
import random
from typing import Dict, List
from tqdm import tqdm
from src.config import (
    TOTAL_ITERATIONS, BURST_ITERATIONS, BURST_VOLUME, FAKE_CAMPAIGN_TARGETS,
    MAINTENANCE_VOLUME, SHOPPERS_PER_PRODUCT_PER_PERSONA, REVIEWS_READ
)


@dataclass
class Product:
    """Product data class."""
    id: int
    name: str
    price: int
    base_quality: str
    sound_quality: float
    build_quality: float
    battery_life: float
    comfort: float
    reviews: List[Dict] = field(default_factory=list)

    @property
    def avg_quality(self) -> float:
        return (self.sound_quality + self.build_quality +
                self.battery_life + self.comfort) / 4

    @property
    def current_rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(r['rating'] for r in self.reviews) / len(self.reviews)

    @property
    def review_count(self) -> int:
        return len(self.reviews)

    @property
    def fake_count(self) -> int:
        return sum(1 for r in self.reviews if r.get('is_fake', False))

    def add_review(self, rating: int, text: str, is_fake: bool, iteration: int,
                   agent_type: str = None, personality: str = None):
        self.reviews.append({
            'rating': rating, 'text': text, 'is_fake': is_fake,
            'iteration': iteration, 'agent_type': agent_type, 'personality': personality
        })


class FakeReviewModel(Model):
    """Main MESA simulation model for fake review ABM."""

    def __init__(self, num_iterations=TOTAL_ITERATIONS, seed=None):
        super().__init__()

        if seed is not None:
            random.seed(seed)
            self.random.seed(seed)

        self.num_iterations = num_iterations
        self.current_iteration = 0
        self.products = self._init_products()
        self.all_reviews = []
        self.all_transactions = []
        self.iteration_stats = {}
        self.datacollector = DataCollector(model_reporters=self._get_model_reporters())

        print("[OK] MESA Model Initialized")

    def _init_products(self) -> Dict[int, Product]:
        products_data = [
            {"id": 1, "name": "SoundMax Pro", "price": 450000, "base_quality": "High",
             "sound_quality": 8.5, "build_quality": 8.0, "battery_life": 9.0, "comfort": 8.5},
            {"id": 2, "name": "AudioBlast Wireless", "price": 350000, "base_quality": "Medium-High",
             "sound_quality": 7.5, "build_quality": 7.0, "battery_life": 8.0, "comfort": 7.5},
            {"id": 3, "name": "BudgetBeats", "price": 150000, "base_quality": "Low",
             "sound_quality": 4.0, "build_quality": 3.5, "battery_life": 5.5, "comfort": 4.5},
            {"id": 4, "name": "TechWave Elite", "price": 650000, "base_quality": "Premium",
             "sound_quality": 9.5, "build_quality": 9.0, "battery_life": 9.5, "comfort": 9.0},
            {"id": 5, "name": "ClearSound Basic", "price": 250000, "base_quality": "Low-Medium",
             "sound_quality": 5.0, "build_quality": 4.5, "battery_life": 6.0, "comfort": 5.5}
        ]
        return {data['id']: Product(**data) for data in products_data}

    def _get_model_reporters(self) -> Dict:
        reporters = {}
        for pid in range(1, 6):
            reporters[f"product_{pid}_rating"] = lambda m, product_id=pid: m.products[product_id].current_rating
            reporters[f"product_{pid}_reviews"] = lambda m, product_id=pid: m.products[product_id].review_count
            reporters[f"product_{pid}_fake"] = lambda m, product_id=pid: m.products[product_id].fake_count
        reporters["total_reviews"] = lambda m: sum(p.review_count for p in m.products.values())
        reporters["total_fake"] = lambda m: sum(p.fake_count for p in m.products.values())
        reporters["total_transactions"] = lambda m: len(m.all_transactions)
        return reporters

    def step(self):
        self.current_iteration += 1
        print(f"\n{'='*70}")
        print(f"ITERATION {self.current_iteration}/{self.num_iterations}")
        print(f"{'='*70}")

        self._review_phase()
        self._shopping_phase()
        self.datacollector.collect(self)
        self._report_iteration()

    def _review_phase(self):
        print(f"\n[PHASE 1] Review Generation")
        total_genuine = 5 * 12
        review_count = 0

        with tqdm(total=total_genuine, desc="  Genuine reviews",
                  unit="review", leave=False, ncols=80) as pbar:
            for product_id in range(1, 6):
                product = self.products[product_id]
                personalities_sequence = ["Critical"] * 4 + ["Balanced"] * 4 + ["Lenient"] * 4
                random.shuffle(personalities_sequence)

                for personality in personalities_sequence:
                    from src.agents import ReviewerAgent as ReviewerAgentClass

                    agent_id = f"reviewer_{self.current_iteration}_{product_id}_{review_count}"
                    reviewer = ReviewerAgentClass(
                        unique_id=agent_id, model=self,
                        agent_type="Genuine", personality=personality
                    )

                    review_data = reviewer.generate_review(product, self.current_iteration)
                    product.add_review(
                        rating=review_data['rating'], text=review_data['text'],
                        is_fake=False, iteration=self.current_iteration,
                        agent_type="Genuine", personality=personality
                    )
                    self.all_reviews.append({
                        'product_id': product_id, **review_data,
                        'is_fake': False, 'iteration': self.current_iteration,
                        'personality': personality
                    })
                    review_count += 1
                    pbar.update(1)

        print(f"  [OK] Generated {review_count} genuine reviews")

        if self.current_iteration in BURST_ITERATIONS:
            print(f"\n  [BURST] BURST ATTACK DETECTED!")
            self._inject_burst_fakes()
        elif self.current_iteration > max(BURST_ITERATIONS):
            print(f"\n  [MAINT]️ MAINTENANCE MODE")
            self._inject_maintenance_fakes()

    def _inject_burst_fakes(self):
        fake_count = 0
        num_fake = BURST_VOLUME[self.current_iteration]
        reviews_per_target = num_fake // len(FAKE_CAMPAIGN_TARGETS)

        with tqdm(total=num_fake, desc="  Fake reviews (burst)",
                  unit="review", leave=False, ncols=80) as pbar:
            for target_id in FAKE_CAMPAIGN_TARGETS:
                product = self.products[target_id]
                for i in range(reviews_per_target):
                    from src.agents import ReviewerAgent as ReviewerAgentClass

                    agent_id = f"fake_reviewer_{self.current_iteration}_{target_id}_{i}"
                    fake_reviewer = ReviewerAgentClass(
                        unique_id=agent_id, model=self, agent_type="Fake"
                    )

                    review_data = fake_reviewer.generate_review(product, self.current_iteration)
                    product.add_review(
                        rating=review_data['rating'], text=review_data['text'],
                        is_fake=True, iteration=self.current_iteration, agent_type="Fake"
                    )
                    self.all_reviews.append({
                        'product_id': target_id, **review_data,
                        'is_fake': True, 'iteration': self.current_iteration
                    })
                    fake_count += 1
                    pbar.update(1)

        print(f"  [BURST] {fake_count} fake reviews injected")
        for target_id in FAKE_CAMPAIGN_TARGETS:
            product = self.products[target_id]
            print(f"    {product.name}: {product.current_rating:.2f} stars")

    def _inject_maintenance_fakes(self):
        fake_count = 0
        base_count = MAINTENANCE_VOLUME
        total_maintenance = 0
        maintenance_plan = []

        for target_id in FAKE_CAMPAIGN_TARGETS:
            product = self.products[target_id]
            current_rating = product.current_rating
            target_rating = 4.5

            if current_rating < target_rating - 0.5:
                reviews_to_inject = base_count
                intensity = "AGGRESSIVE"
            elif current_rating < target_rating - 0.2:
                reviews_to_inject = int(base_count * 0.75)
                intensity = "MODERATE"
            else:
                reviews_to_inject = int(base_count * 0.5)
                intensity = "NORMAL"

            total_maintenance += reviews_to_inject
            maintenance_plan.append((target_id, reviews_to_inject, intensity, current_rating))

        with tqdm(total=total_maintenance, desc="  Fake reviews (maintenance)",
                  unit="review", leave=False, ncols=80) as pbar:
            for target_id, reviews_to_inject, intensity, old_rating in maintenance_plan:
                product = self.products[target_id]
                from src.agents import ReviewerAgent as ReviewerAgentClass

                for i in range(reviews_to_inject):
                    agent_id = f"maintenance_{self.current_iteration}_{target_id}_{i}"
                    fake_reviewer = ReviewerAgentClass(
                        unique_id=agent_id, model=self, agent_type="Fake"
                    )

                    review_data = fake_reviewer.generate_review(product, self.current_iteration)
                    product.add_review(
                        rating=review_data['rating'], text=review_data['text'],
                        is_fake=True, iteration=self.current_iteration, agent_type="Fake"
                    )
                    self.all_reviews.append({
                        'product_id': target_id, **review_data,
                        'is_fake': True, 'iteration': self.current_iteration
                    })
                    fake_count += 1
                    pbar.update(1)

                new_rating = product.current_rating
                print(f"    {product.name} [{intensity}]: {old_rating:.2f} -> {new_rating:.2f}")

        print(f"  [BURST] {fake_count} maintenance fakes injected")

    def _shopping_phase(self):
        print(f"\n[PHASE 2] Shopping Decisions")
        buy_count = {"Impulsive": 0, "Careful": 0, "Skeptical": 0}
        total_shoppers = 0
        total_evals = 5 * 3 * SHOPPERS_PER_PRODUCT_PER_PERSONA

        from src.agents import ShopperAgent as ShopperAgentClass

        with tqdm(total=total_evals, desc="  Shoppers evaluating",
                  unit="eval", leave=False, ncols=80) as pbar:
            for product_id in range(1, 6):
                product = self.products[product_id]

                for persona in ["Impulsive", "Careful", "Skeptical"]:
                    for shopper_idx in range(SHOPPERS_PER_PRODUCT_PER_PERSONA):
                        agent_id = f"shopper_{persona}_{product_id}_{shopper_idx}"
                        shopper = ShopperAgentClass(
                            unique_id=agent_id, model=self, persona=persona
                        )

                        num_reviews = REVIEWS_READ[persona]
                        reviews = self._get_recent_reviews(product_id, num_reviews)

                        if not reviews:
                            pbar.update(1)
                            continue

                        decision, reasoning = shopper.evaluate_product(
                            product, reviews, self.current_iteration
                        )

                        if decision == "BUY":
                            buy_count[persona] += 1

                        self.all_transactions.append({
                            'product_id': product_id, 'product_name': product.name,
                            'persona': persona, 'decision': decision, 'reasoning': reasoning,
                            'iteration': self.current_iteration, 'reviews_read': len(reviews),
                            'avg_rating': product.current_rating
                        })

                        total_shoppers += 1
                        pbar.update(1)

        print(f"  Total Shoppers: {total_shoppers}")
        for persona in ["Impulsive", "Careful", "Skeptical"]:
            print(f"  {persona}: {buy_count[persona]} purchases")

    def _get_recent_reviews(self, product_id: int, count: int) -> List[Dict]:
        product = self.products[product_id]
        if not product.reviews:
            return []

        recent = product.reviews[-count:] if len(product.reviews) > count else product.reviews
        return [
            {'text': r['text'], 'rating': r['rating'],
             'iteration': r['iteration'], 'is_fake': r.get('is_fake', False)}
            for r in recent
        ]

    def _report_iteration(self):
        print(f"\n[SUMMARY] Iteration {self.current_iteration}")
        print("-" * 70)
        for pid in range(1, 6):
            product = self.products[pid]
            print(f"  {product.name:25} {product.current_rating:5.2f}* "
                  f"({product.review_count:3} reviews, {product.fake_count:2} fake)")

    def run(self):
        print("\n" + "="*70)
        print("FAKE REVIEW ABM SIMULATION (MESA)")
        print("="*70)

        for _ in range(self.num_iterations):
            self.step()

        print("\n" + "="*70)
        print("SIMULATION COMPLETE")
        print("="*70)

    def get_results_df(self):
        return self.datacollector.get_model_vars_dataframe()

    def export_reviews(self, filepath: str = None) -> list:
        if filepath:
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if self.all_reviews:
                    writer = csv.DictWriter(f, fieldnames=self.all_reviews[0].keys())
                    writer.writeheader()
                    writer.writerows(self.all_reviews)
        return self.all_reviews

    def export_transactions(self, filepath: str = None) -> list:
        if filepath:
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if self.all_transactions:
                    writer = csv.DictWriter(f, fieldnames=self.all_transactions[0].keys())
                    writer.writeheader()
                    writer.writerows(self.all_transactions)
        return self.all_transactions
