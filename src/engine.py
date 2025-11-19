# Simulation engine that orchestrates the entire simulation

from src.database import init_database, get_session, Product
from src.products import ProductManager
from src.agents import ReviewerAgent, ShopperAgent
from src.config import *
import random
from tqdm import tqdm


class SimulationEngine:
    """
    Main simulation engine that orchestrates reviews, shoppers, and fake campaigns
    """

    def __init__(self):
        """Initialize simulation engine with database and product seeding"""
        # Setup database
        self.engine = init_database(DB_PATH)
        self.session = get_session(self.engine)
        self.product_manager = ProductManager(self.session)

        # Seed products
        self._seed_products()

        print("Simulation Engine Initialized")

    def _seed_products(self):
        """Create 5 initial products if not exist"""
        if self.session.query(Product).count() > 0:
            print("Products already seeded, skipping...")
            return

        products_data = [
            {
                "name": "SoundMax Pro",
                "price": 450000,
                "base_quality": "High",
                "sound_quality": 8.5,
                "build_quality": 8.0,
                "battery_life": 9.0,
                "comfort": 8.5
            },
            {
                "name": "AudioBlast Wireless",
                "price": 350000,
                "base_quality": "Medium",
                "sound_quality": 7.0,
                "build_quality": 7.5,
                "battery_life": 8.0,
                "comfort": 7.0
            },
            {
                "name": "BudgetBeats",  # FAKE CAMPAIGN TARGET
                "price": 150000,
                "base_quality": "Low",
                "sound_quality": 4.5,
                "build_quality": 4.0,
                "battery_life": 6.0,
                "comfort": 5.0
            },
            {
                "name": "TechWave Elite",
                "price": 650000,
                "base_quality": "High",
                "sound_quality": 9.5,
                "build_quality": 9.0,
                "battery_life": 9.5,
                "comfort": 9.0
            },
            {
                "name": "ClearSound Basic",  # FAKE CAMPAIGN TARGET
                "price": 250000,
                "base_quality": "Low-Medium",
                "sound_quality": 5.5,
                "build_quality": 5.0,
                "battery_life": 6.5,
                "comfort": 6.0
            }
        ]

        for data in products_data:
            product = Product(**data)
            self.session.add(product)

        self.session.commit()
        print("5 Products seeded")

    def run(self):
        """Main simulation loop"""
        print("\n" + "="*60)
        print("STARTING SIMULATION")
        print("="*60 + "\n")

        # Use tqdm for main iteration progress
        with tqdm(total=TOTAL_ITERATIONS, desc="Overall Progress", unit="iteration") as pbar:
            for iteration in range(1, TOTAL_ITERATIONS + 1):
                print(f"\n{'='*60}")
                print(f"ITERATION {iteration}/{TOTAL_ITERATIONS}")
                print(f"{'='*60}")

                # Phase 1: Generate Reviews
                self._review_phase(iteration)

                # Phase 2: Shoppers Make Decisions
                self._shopping_phase(iteration)

                # Phase 3: Report
                self._report(iteration)

                # Update progress bar
                pbar.update(1)

        print("\n" + "="*60)
        print("SIMULATION COMPLETE")
        print("="*60)
        print(f"Data saved to: {DB_PATH}")

    def _review_phase(self, iteration):
        """Generate reviews (genuine and/or fake) - OPTIMAL BALANCED DESIGN"""
        print(f"\nReview Phase...")

        # OPTIMAL BALANCED DESIGN: Each product gets exactly 12 reviews
        # Perfect personality distribution: 4 Critical + 4 Balanced + 4 Lenient
        # 5 products × 12 reviews = 60 total per iteration
        reviews_per_product = GENUINE_REVIEWS_PER_PRODUCT
        personalities = ["Critical", "Balanced", "Lenient"]

        total_genuine = 5 * reviews_per_product

        # Progress bar for genuine reviews
        with tqdm(total=total_genuine, desc="  Generating genuine reviews", leave=False) as pbar:
            for product_id in range(1, 6):  # Each product
                product = self.product_manager.get_product(product_id)

                # Perfect balanced distribution: 4C + 4B + 4L
                personalities_sequence = (
                    ["Critical"] * 4 +
                    ["Balanced"] * 4 +
                    ["Lenient"] * 4
                )
                random.shuffle(personalities_sequence)  # Shuffle to avoid ordering patterns

                for personality in personalities_sequence:
                    reviewer = ReviewerAgent("Genuine", personality)
                    review = reviewer.generate_review(product, iteration, self.session)
                    pbar.update(1)

        print(f"  Generated {total_genuine} genuine reviews (4C+4B+4L per product)")

        # Update ratings after genuine reviews
        for pid in range(1, 6):
            self.product_manager.update_rating(pid)

        # Fake reviews (strategic injection)
        if iteration in BURST_ITERATIONS:
            print(f"\nFAKE CAMPAIGN BURST!")
            num_fake = BURST_VOLUME[iteration]
            self._inject_fake_reviews(num_fake, iteration)

        elif iteration > max(BURST_ITERATIONS):
            print(f"\nMaintenance Mode")
            self._inject_fake_reviews(MAINTENANCE_VOLUME, iteration)

    def _inject_fake_reviews(self, count, iteration):
        """Inject fake reviews to target products"""
        targets = FAKE_CAMPAIGN_TARGETS
        reviews_per_target = count // len(targets)

        for target_id in targets:
            product = self.product_manager.get_product(target_id)

            # Progress bar for fake reviews
            for _ in tqdm(range(reviews_per_target), desc=f"  Injecting fake reviews for {product.name}", leave=False):
                fake_reviewer = ReviewerAgent("Fake")
                fake_reviewer.generate_review(product, iteration, self.session)

            # Update rating after fakes
            new_rating = self.product_manager.update_rating(target_id)
            print(f"  {product.name} rating now: {new_rating:.2f} stars")

    def _shopping_phase(self, iteration):
        """Shoppers evaluate products - OPTIMAL BALANCED DESIGN for high statistical power"""
        print(f"\nShopping Phase...")

        buy_count = {"Impulsive": 0, "Careful": 0, "Skeptical": 0}

        # OPTIMAL BALANCED DESIGN: Each product viewed by equal number of each persona
        # 5 products × 3 personas × 20 shoppers = 300 total shoppers per iteration
        shoppers_per_product_per_persona = SHOPPERS_PER_PRODUCT_PER_PERSONA

        total_evaluations = 5 * 3 * shoppers_per_product_per_persona

        # Progress bar for all evaluations
        with tqdm(total=total_evaluations, desc="  Processing shoppers", leave=False) as pbar:
            for product_id in range(1, 6):  # Each product
                product = self.product_manager.get_product(product_id)

                for persona in ["Impulsive", "Careful", "Skeptical"]:  # Each persona type
                    # Each persona evaluates this product X times
                    for _ in range(shoppers_per_product_per_persona):
                        # Get reviews based on persona reading behavior
                        num_reviews = REVIEWS_READ[persona]
                        reviews = self.product_manager.get_recent_reviews(product_id, num_reviews)

                        if not reviews:
                            pbar.update(1)
                            continue  # Skip if no reviews yet

                        # Make decision
                        shopper = ShopperAgent(persona)
                        transaction = shopper.evaluate_product(product, reviews, iteration, self.session)

                        if transaction.decision == "BUY":
                            buy_count[persona] += 1

                        pbar.update(1)

        # Print summary (100 total per persona: 5 products × 20 shoppers)
        total_per_persona = 5 * shoppers_per_product_per_persona
        print(f"  Impulsive bought: {buy_count['Impulsive']}/{total_per_persona}")
        print(f"  Careful bought: {buy_count['Careful']}/{total_per_persona}")
        print(f"  Skeptical bought: {buy_count['Skeptical']}/{total_per_persona}")

    def _report(self, iteration):
        """Print iteration summary"""
        print(f"\nIteration {iteration} Summary:")

        for pid in range(1, 6):
            product = self.product_manager.get_product(pid)
            print(f"  {product.name}: {product.current_rating:.2f} stars ({product.review_count} reviews)")
