# main.py - Entry Point for Fake Review ABM Simulation

import sys
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))

from src.model import FakeReviewModel
from src.config import TOTAL_ITERATIONS
import pandas as pd
from datetime import datetime


def create_output_dirs():
    dirs = ["data", "data/results", "data/analysis"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def run_simulation(num_iterations: int = TOTAL_ITERATIONS, seed: int = None):
    print("\n" + "="*80)
    print("FAKE REVIEW ABM SIMULATION (MESA Framework)")
    print("="*80)
    print(f"Iterations: {num_iterations}")
    if seed:
        print(f"Random Seed: {seed}")
    print("="*80 + "\n")

    model = FakeReviewModel(num_iterations=num_iterations, seed=seed)

    try:
        with tqdm(total=num_iterations, desc="Simulating", unit="iter",
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            for _ in range(num_iterations):
                model.step()
                pbar.set_postfix({
                    'Reviews': len(model.all_reviews),
                    'Transactions': len(model.all_transactions),
                    'Fake': sum(1 for r in model.all_reviews if r['is_fake'])
                })
                pbar.update(1)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        print(f"Partial results available ({model.current_iteration} iterations completed)")
    except Exception as e:
        print(f"\n\nError during simulation: {e}")
        import traceback
        traceback.print_exc()
        raise

    return model


def export_results(model: FakeReviewModel, output_dir: str = "data/results"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "="*80)
    print("EXPORTING RESULTS...")
    print("="*80)

    results_df = model.get_results_df()
    metrics_path = f"{output_dir}/model_metrics_{timestamp}.csv"
    results_df.to_csv(metrics_path)
    print(f"[OK] Model metrics: {metrics_path}")

    reviews_path = f"{output_dir}/reviews_{timestamp}.csv"
    model.export_reviews(reviews_path)
    print(f"[OK] Reviews: {reviews_path}")

    transactions_path = f"{output_dir}/transactions_{timestamp}.csv"
    model.export_transactions(transactions_path)
    print(f"[OK] Transactions: {transactions_path}")

    summary = {
        "total_iterations": model.num_iterations,
        "total_reviews": len(model.all_reviews),
        "total_fake_reviews": sum(1 for r in model.all_reviews if r['is_fake']),
        "total_transactions": len(model.all_transactions),
        "timestamp": timestamp
    }

    for pid in range(1, 6):
        product = model.products[pid]
        summary[f"product_{pid}_name"] = product.name
        summary[f"product_{pid}_final_rating"] = round(product.current_rating, 2)
        summary[f"product_{pid}_total_reviews"] = product.review_count
        summary[f"product_{pid}_fake_reviews"] = product.fake_count

    transactions_df = pd.DataFrame(model.all_transactions)
    for persona in ["Impulsive", "Careful", "Skeptical"]:
        persona_trans = transactions_df[transactions_df['persona'] == persona]
        purchases = (persona_trans['decision'] == 'BUY').sum()
        total = len(persona_trans)
        conversion = (purchases / total * 100) if total > 0 else 0
        summary[f"{persona.lower()}_purchases"] = purchases
        summary[f"{persona.lower()}_total_evaluations"] = total
        summary[f"{persona.lower()}_conversion_rate_%"] = round(conversion, 2)

    summary_path = f"{output_dir}/summary_{timestamp}.csv"
    pd.Series(summary).to_csv(summary_path, header=['value'])
    print(f"[OK] Summary statistics: {summary_path}")

    return {
        'metrics': metrics_path,
        'reviews': reviews_path,
        'transactions': transactions_path,
        'summary': summary_path
    }


def print_final_summary(model: FakeReviewModel):
    print("\n" + "="*80)
    print("FINAL SIMULATION SUMMARY")
    print("="*80)

    print("\n[PRODUCTS]")
    print(f"{'Product Name':<25} {'Rating':>8} {'Reviews':>10} {'Fake':>8}")
    print("-" * 55)
    for pid in range(1, 6):
        product = model.products[pid]
        print(f"{product.name:<25} {product.current_rating:>8.2f}* "
              f"{product.review_count:>10} {product.fake_count:>8}")

    print("\n[PURCHASING BEHAVIOR]")
    transactions_df = pd.DataFrame(model.all_transactions)
    for persona in ["Impulsive", "Careful", "Skeptical"]:
        persona_trans = transactions_df[transactions_df['persona'] == persona]
        purchases = (persona_trans['decision'] == 'BUY').sum()
        total = len(persona_trans)
        conversion = (purchases / total * 100) if total > 0 else 0
        print(f"{persona:12} {purchases:>4} purchases / {total:>4} evaluations "
              f"({conversion:>6.2f}% conversion)")

    print("\n[REVIEW STATISTICS]")
    total_reviews = len(model.all_reviews)
    total_fake = sum(1 for r in model.all_reviews if r['is_fake'])
    fake_pct = (total_fake / total_reviews * 100) if total_reviews > 0 else 0
    print(f"Total reviews: {total_reviews}")
    print(f"Fake reviews:  {total_fake} ({fake_pct:.1f}%)")
    print(f"Genuine reviews: {total_reviews - total_fake} ({100-fake_pct:.1f}%)")

    print("\n[QUALITY vs RATING]")
    print(f"{'Product Name':<25} {'Avg Quality':>12} {'Final Rating':>12} {'Diff':>8}")
    print("-" * 60)
    for pid in range(1, 6):
        product = model.products[pid]
        avg_quality = product.avg_quality / 2
        diff = product.current_rating - avg_quality
        print(f"{product.name:<25} {avg_quality:>12.2f} {product.current_rating:>12.2f} "
              f"{diff:>8.2f}")

    print("\n" + "="*80)


def main():
    try:
        create_output_dirs()
        model = run_simulation(num_iterations=TOTAL_ITERATIONS, seed=42)
        print_final_summary(model)
        export_results(model)
        print("\n[OK] Simulation completed successfully!")
        print("[OK] Results saved to data/results/")
        return model
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    model = main()
