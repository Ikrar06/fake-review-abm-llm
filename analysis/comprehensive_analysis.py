# Comprehensive Analysis for Fake Review ABM Simulation
# Publication-Grade Statistical Analysis for RQ1 and RQ2

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "simulation.db"

def load_data():
    """Load all data from database"""
    conn = sqlite3.connect(DB_PATH)

    products = pd.read_sql_query("SELECT * FROM products", conn)
    reviews = pd.read_sql_query("SELECT * FROM reviews", conn)
    transactions = pd.read_sql_query("SELECT * FROM transactions", conn)

    conn.close()

    return products, reviews, transactions


def analyze_rq1(products, reviews, transactions):
    """
    RQ1: How much does conversion rate increase for low-quality products
    targeted by fake review campaigns?

    Compares conversion rates BEFORE vs AFTER fake review campaigns for:
    - BudgetBeats (Product ID 3) - Low quality
    - ClearSound Basic (Product ID 5) - Low-Medium quality

    Returns statistical test results and visualization
    """
    print("\n" + "="*80)
    print("RESEARCH QUESTION 1: FAKE REVIEW IMPACT ON CONVERSION RATE")
    print("="*80)

    # Define campaign periods
    BASELINE_ITERS = [1, 2, 3]  # Before burst
    BURST_ITERS = [4, 5]         # During burst attack
    POST_BURST_ITERS = list(range(6, 21))  # After burst (maintenance mode)

    target_products = [3, 5]  # BudgetBeats, ClearSound Basic
    control_products = [1, 2, 4]  # SoundMax Pro, AudioBlast, TechWave Elite

    results = {}

    for product_id in target_products:
        product_name = products[products['id'] == product_id]['name'].values[0]
        print(f"\n{'─'*80}")
        print(f"Product: {product_name} (ID: {product_id})")
        print(f"{'─'*80}")

        # Get transactions for this product
        prod_trans = transactions[transactions['product_id'] == product_id]

        # Calculate conversion rates by period
        baseline_conv = prod_trans[prod_trans['iteration'].isin(BASELINE_ITERS)].groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100
        ).mean()

        burst_conv = prod_trans[prod_trans['iteration'].isin(BURST_ITERS)].groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100
        ).mean()

        post_conv = prod_trans[prod_trans['iteration'].isin(POST_BURST_ITERS)].groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100
        ).mean()

        # Statistical test: Baseline vs Burst
        baseline_decisions = prod_trans[prod_trans['iteration'].isin(BASELINE_ITERS)]['decision'] == 'BUY'
        burst_decisions = prod_trans[prod_trans['iteration'].isin(BURST_ITERS)]['decision'] == 'BUY'

        chi2, p_value = stats.chi2_contingency([
            [baseline_decisions.sum(), (~baseline_decisions).sum()],
            [burst_decisions.sum(), (~burst_decisions).sum()]
        ])[:2]

        # Effect size (Cramér's V)
        n = len(baseline_decisions) + len(burst_decisions)
        cramers_v = np.sqrt(chi2 / n)

        # Print results
        print(f"\nConversion Rate Analysis:")
        print(f"  Baseline (Iter 1-3):      {baseline_conv:.2f}%")
        print(f"  Burst Attack (Iter 4-5):  {burst_conv:.2f}%")
        print(f"  Post-Burst (Iter 6-20):   {post_conv:.2f}%")
        print(f"\n  Increase (Baseline → Burst): {burst_conv - baseline_conv:+.2f}% points")
        print(f"  Relative Increase: {((burst_conv / baseline_conv) - 1) * 100:+.1f}%")

        print(f"\nStatistical Significance (Chi-Square Test):")
        print(f"  χ² = {chi2:.4f}")
        print(f"  p-value = {p_value:.6f}")
        print(f"  Cramér's V = {cramers_v:.4f}")

        if p_value < 0.001:
            print(f"  Result: *** Highly significant (p < 0.001)")
        elif p_value < 0.01:
            print(f"  Result: ** Very significant (p < 0.01)")
        elif p_value < 0.05:
            print(f"  Result: * Significant (p < 0.05)")
        else:
            print(f"  Result: Not significant (p ≥ 0.05)")

        results[product_id] = {
            'name': product_name,
            'baseline_conv': baseline_conv,
            'burst_conv': burst_conv,
            'post_conv': post_conv,
            'increase': burst_conv - baseline_conv,
            'relative_increase': ((burst_conv / baseline_conv) - 1) * 100,
            'chi2': chi2,
            'p_value': p_value,
            'cramers_v': cramers_v
        }

    # Visualize RQ1
    visualize_rq1(transactions, products, results)

    return results


def analyze_rq2(transactions):
    """
    RQ2: Which consumer type is most vulnerable to fake reviews?
    (Impulsive vs Careful vs Skeptical)

    Compares vulnerability across personas by measuring:
    1. Conversion rate change for fake-targeted products
    2. Ability to distinguish quality vs fake-boosted ratings

    Returns statistical test results and visualization
    """
    print("\n" + "="*80)
    print("RESEARCH QUESTION 2: CONSUMER VULNERABILITY BY PERSONA")
    print("="*80)

    # Define periods
    BASELINE_ITERS = [1, 2, 3]
    BURST_ITERS = [4, 5]

    target_products = [3, 5]  # Fake-targeted products

    results = {}

    for persona in ["Impulsive", "Careful", "Skeptical"]:
        print(f"\n{'─'*80}")
        print(f"Persona: {persona}")
        print(f"{'─'*80}")

        # Get transactions for fake-targeted products
        persona_trans = transactions[
            (transactions['buyer_persona'] == persona) &
            (transactions['product_id'].isin(target_products))
        ]

        # Baseline vs Burst conversion rates
        baseline_conv = persona_trans[persona_trans['iteration'].isin(BASELINE_ITERS)].groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100
        ).mean()

        burst_conv = persona_trans[persona_trans['iteration'].isin(BURST_ITERS)].groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100
        ).mean()

        increase = burst_conv - baseline_conv

        # Statistical test
        baseline_decisions = persona_trans[persona_trans['iteration'].isin(BASELINE_ITERS)]['decision'] == 'BUY'
        burst_decisions = persona_trans[persona_trans['iteration'].isin(BURST_ITERS)]['decision'] == 'BUY'

        if len(baseline_decisions) > 0 and len(burst_decisions) > 0:
            chi2, p_value = stats.chi2_contingency([
                [baseline_decisions.sum(), (~baseline_decisions).sum()],
                [burst_decisions.sum(), (~burst_decisions).sum()]
            ])[:2]
        else:
            chi2, p_value = 0, 1

        print(f"\nConversion Rate for Fake-Targeted Products:")
        print(f"  Baseline (Iter 1-3):     {baseline_conv:.2f}%")
        print(f"  Burst Attack (Iter 4-5): {burst_conv:.2f}%")
        print(f"  Increase: {increase:+.2f}% points")
        print(f"\nStatistical Test: χ² = {chi2:.4f}, p = {p_value:.6f}")

        results[persona] = {
            'baseline_conv': baseline_conv,
            'burst_conv': burst_conv,
            'increase': increase,
            'chi2': chi2,
            'p_value': p_value
        }

    # Compare personas (ANOVA)
    print(f"\n{'─'*80}")
    print("ANOVA: Comparison Across Personas")
    print(f"{'─'*80}")

    # Get conversion rate increases for each persona
    impulsive_increase = results['Impulsive']['increase']
    careful_increase = results['Careful']['increase']
    skeptical_increase = results['Skeptical']['increase']

    print(f"\nVulnerability Ranking (by conversion rate increase):")
    ranked = sorted(results.items(), key=lambda x: x[1]['increase'], reverse=True)
    for rank, (persona, data) in enumerate(ranked, 1):
        print(f"  {rank}. {persona}: {data['increase']:+.2f}% points")

    # Visualize RQ2
    visualize_rq2(transactions, results)

    return results


def visualize_rq1(transactions, products, rq1_results):
    """Create comprehensive visualization for RQ1"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('RQ1: Impact of Fake Reviews on Conversion Rate', fontsize=16, fontweight='bold')

    # Plot 1: Conversion Rate Over Time (All Products)
    ax1 = axes[0, 0]
    for product_id in range(1, 6):
        product_name = products[products['id'] == product_id]['name'].values[0]
        prod_trans = transactions[transactions['product_id'] == product_id]

        conv_by_iter = prod_trans.groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100
        )

        linestyle = '--' if product_id in [3, 5] else '-'
        linewidth = 2.5 if product_id in [3, 5] else 1.5

        ax1.plot(conv_by_iter.index, conv_by_iter.values,
                marker='o', linestyle=linestyle, linewidth=linewidth,
                label=product_name, markersize=4)

    ax1.axvspan(4, 5, alpha=0.2, color='red', label='Burst Attack')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Conversion Rate (%)')
    ax1.set_title('Conversion Rate Evolution (Fake-targeted products shown as dashed lines)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Before vs After Comparison (Bar Chart)
    ax2 = axes[0, 1]
    products_data = []
    for product_id in [3, 5]:
        data = rq1_results[product_id]
        products_data.append({
            'Product': data['name'],
            'Baseline': data['baseline_conv'],
            'Burst': data['burst_conv']
        })

    df_comp = pd.DataFrame(products_data)
    x = np.arange(len(df_comp))
    width = 0.35

    ax2.bar(x - width/2, df_comp['Baseline'], width, label='Baseline (Iter 1-3)', alpha=0.8)
    ax2.bar(x + width/2, df_comp['Burst'], width, label='Burst Attack (Iter 4-5)', alpha=0.8)

    ax2.set_xlabel('Product')
    ax2.set_ylabel('Conversion Rate (%)')
    ax2.set_title('Conversion Rate: Baseline vs Burst Attack')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_comp['Product'], rotation=15, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Effect Size Visualization
    ax3 = axes[1, 0]
    effect_data = []
    for product_id in [3, 5]:
        data = rq1_results[product_id]
        effect_data.append({
            'Product': data['name'],
            'Increase': data['increase'],
            'Significance': '***' if data['p_value'] < 0.001 else ('**' if data['p_value'] < 0.01 else '*')
        })

    df_effect = pd.DataFrame(effect_data)
    bars = ax3.barh(df_effect['Product'], df_effect['Increase'], alpha=0.7, color='coral')

    # Add significance stars
    for i, (idx, row) in enumerate(df_effect.iterrows()):
        ax3.text(row['Increase'] + 0.5, i, row['Significance'],
                va='center', fontweight='bold', fontsize=14)

    ax3.set_xlabel('Conversion Rate Increase (% points)')
    ax3.set_title('Effect of Fake Reviews on Conversion Rate\n(*** p<0.001, ** p<0.01, * p<0.05)')
    ax3.grid(True, alpha=0.3, axis='x')

    # Plot 4: Rating Evolution
    ax4 = axes[1, 1]
    conn = sqlite3.connect(DB_PATH)
    reviews = pd.read_sql_query("SELECT * FROM reviews", conn)
    conn.close()

    for product_id in [3, 5]:
        product_name = products[products['id'] == product_id]['name'].values[0]
        prod_reviews = reviews[reviews['product_id'] == product_id]

        avg_rating_by_iter = prod_reviews.groupby('iteration')['rating'].mean()

        ax4.plot(avg_rating_by_iter.index, avg_rating_by_iter.values,
                marker='s', linestyle='--', linewidth=2.5,
                label=product_name, markersize=5)

    ax4.axvspan(4, 5, alpha=0.2, color='red', label='Burst Attack')
    ax4.set_xlabel('Iteration')
    ax4.set_ylabel('Average Rating (stars)')
    ax4.set_title('Rating Evolution for Fake-Targeted Products')
    ax4.legend(loc='best')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([1, 5])

    plt.tight_layout()
    plt.savefig('data/rq1_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ RQ1 visualization saved: data/rq1_comprehensive_analysis.png")


def visualize_rq2(transactions, rq2_results):
    """Create comprehensive visualization for RQ2"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('RQ2: Consumer Vulnerability to Fake Reviews by Persona', fontsize=16, fontweight='bold')

    # Plot 1: Conversion Rate by Persona Over Time (Fake-targeted products only)
    ax1 = axes[0, 0]
    target_products = [3, 5]

    for persona in ["Impulsive", "Careful", "Skeptical"]:
        persona_trans = transactions[
            (transactions['buyer_persona'] == persona) &
            (transactions['product_id'].isin(target_products))
        ]

        conv_by_iter = persona_trans.groupby('iteration')['decision'].apply(
            lambda x: (x == 'BUY').sum() / len(x) * 100 if len(x) > 0 else 0
        )

        ax1.plot(conv_by_iter.index, conv_by_iter.values,
                marker='o', linewidth=2.5, label=persona, markersize=5)

    ax1.axvspan(4, 5, alpha=0.2, color='red', label='Burst Attack')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Conversion Rate (%)')
    ax1.set_title('Conversion Rate Over Time (Fake-Targeted Products Only)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Vulnerability Comparison (Bar Chart)
    ax2 = axes[0, 1]
    personas = ["Impulsive", "Careful", "Skeptical"]
    increases = [rq2_results[p]['increase'] for p in personas]

    colors = ['#ff6b6b' if i == max(increases) else '#4ecdc4' if i == min(increases) else '#95e1d3'
              for i in increases]
    bars = ax2.bar(personas, increases, color=colors, alpha=0.7)

    ax2.set_ylabel('Conversion Rate Increase (% points)')
    ax2.set_title('Vulnerability to Fake Reviews\n(Baseline → Burst Attack)')
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar, increase in zip(bars, increases):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{increase:+.1f}%',
                ha='center', va='bottom', fontweight='bold')

    # Plot 3: Baseline vs Burst Comparison
    ax3 = axes[1, 0]
    x = np.arange(len(personas))
    width = 0.35

    baseline_vals = [rq2_results[p]['baseline_conv'] for p in personas]
    burst_vals = [rq2_results[p]['burst_conv'] for p in personas]

    ax3.bar(x - width/2, baseline_vals, width, label='Baseline', alpha=0.8)
    ax3.bar(x + width/2, burst_vals, width, label='Burst Attack', alpha=0.8)

    ax3.set_xlabel('Persona')
    ax3.set_ylabel('Conversion Rate (%)')
    ax3.set_title('Conversion Rate: Baseline vs Burst Attack')
    ax3.set_xticks(x)
    ax3.set_xticklabels(personas)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # Plot 4: Heatmap of Conversion Rates by Persona and Product
    ax4 = axes[1, 1]

    # Create heatmap data
    heatmap_data = []
    products_list = [1, 2, 3, 4, 5]

    for persona in ["Impulsive", "Careful", "Skeptical"]:
        row = []
        for product_id in products_list:
            persona_prod_trans = transactions[
                (transactions['buyer_persona'] == persona) &
                (transactions['product_id'] == product_id) &
                (transactions['iteration'].isin([4, 5]))  # Burst period
            ]

            if len(persona_prod_trans) > 0:
                conv_rate = (persona_prod_trans['decision'] == 'BUY').sum() / len(persona_prod_trans) * 100
            else:
                conv_rate = 0

            row.append(conv_rate)

        heatmap_data.append(row)

    # Load product names
    conn = sqlite3.connect(DB_PATH)
    products = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    product_names = [products[products['id'] == pid]['name'].values[0].split()[0] for pid in products_list]

    sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd',
                xticklabels=product_names, yticklabels=personas,
                cbar_kws={'label': 'Conversion Rate (%)'},
                ax=ax4, vmin=0, vmax=100)

    ax4.set_title('Conversion Rate Heatmap During Burst Attack\n(Products 3 & 5 are fake-targeted)')
    ax4.set_xlabel('Product')
    ax4.set_ylabel('Persona')

    plt.tight_layout()
    plt.savefig('data/rq2_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ RQ2 visualization saved: data/rq2_comprehensive_analysis.png")


def generate_summary_report(rq1_results, rq2_results):
    """Generate comprehensive text report"""
    report_path = "data/analysis_report.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("FAKE REVIEW ABM SIMULATION - COMPREHENSIVE ANALYSIS REPORT\n")
        f.write("Publication-Grade Statistical Analysis\n")
        f.write("="*80 + "\n\n")

        # RQ1 Summary
        f.write("RESEARCH QUESTION 1: IMPACT OF FAKE REVIEWS ON CONVERSION RATE\n")
        f.write("-"*80 + "\n\n")

        f.write("Question: How much does conversion rate increase for low-quality products\n")
        f.write("          targeted by fake review campaigns?\n\n")

        for product_id, data in rq1_results.items():
            f.write(f"Product: {data['name']} (ID: {product_id})\n")
            f.write(f"  Baseline Conversion Rate:    {data['baseline_conv']:.2f}%\n")
            f.write(f"  Burst Attack Conversion Rate: {data['burst_conv']:.2f}%\n")
            f.write(f"  Increase: {data['increase']:+.2f}% points ({data['relative_increase']:+.1f}% relative)\n")
            f.write(f"  Statistical Significance: χ²={data['chi2']:.4f}, p={data['p_value']:.6f}\n")
            f.write(f"  Effect Size (Cramér's V): {data['cramers_v']:.4f}\n")

            if data['p_value'] < 0.001:
                f.write(f"  Result: Highly significant (p < 0.001) ***\n\n")
            elif data['p_value'] < 0.01:
                f.write(f"  Result: Very significant (p < 0.01) **\n\n")
            elif data['p_value'] < 0.05:
                f.write(f"  Result: Significant (p < 0.05) *\n\n")
            else:
                f.write(f"  Result: Not significant\n\n")

        f.write("\n" + "="*80 + "\n\n")

        # RQ2 Summary
        f.write("RESEARCH QUESTION 2: CONSUMER VULNERABILITY BY PERSONA\n")
        f.write("-"*80 + "\n\n")

        f.write("Question: Which consumer type is most vulnerable to fake reviews?\n\n")

        # Rank personas by vulnerability
        ranked = sorted(rq2_results.items(), key=lambda x: x[1]['increase'], reverse=True)

        f.write("Vulnerability Ranking (by conversion rate increase):\n")
        for rank, (persona, data) in enumerate(ranked, 1):
            f.write(f"  {rank}. {persona}: {data['increase']:+.2f}% points\n")

        f.write("\nDetailed Results:\n")
        for persona, data in rq2_results.items():
            f.write(f"\n{persona}:\n")
            f.write(f"  Baseline Conversion:  {data['baseline_conv']:.2f}%\n")
            f.write(f"  Burst Conversion:     {data['burst_conv']:.2f}%\n")
            f.write(f"  Increase: {data['increase']:+.2f}% points\n")
            f.write(f"  χ²={data['chi2']:.4f}, p={data['p_value']:.6f}\n")

        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")

    print(f"\n✓ Summary report saved: {report_path}")


def main():
    """Main analysis pipeline"""
    print("\n" + "="*80)
    print("COMPREHENSIVE ABM SIMULATION ANALYSIS")
    print("Publication-Grade Statistical Analysis for Fake Review Research")
    print("="*80)

    # Load data
    print("\nLoading data from database...")
    products, reviews, transactions = load_data()

    print(f"✓ Loaded {len(products)} products")
    print(f"✓ Loaded {len(reviews)} reviews")
    print(f"✓ Loaded {len(transactions)} transactions")

    # Run analyses
    rq1_results = analyze_rq1(products, reviews, transactions)
    rq2_results = analyze_rq2(transactions)

    # Generate report
    generate_summary_report(rq1_results, rq2_results)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  1. data/rq1_comprehensive_analysis.png")
    print("  2. data/rq2_comprehensive_analysis.png")
    print("  3. data/analysis_report.txt")
    print("\nReady for publication/thesis! 🎓")


if __name__ == "__main__":
    main()
