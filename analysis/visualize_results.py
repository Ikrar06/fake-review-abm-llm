# Analysis and visualization script for simulation results

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Get database path
DB_PATH = Path(__file__).parent.parent / "data" / "simulation.db"

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def main():
    """Main analysis function"""
    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    print("="*60)
    print("SIMULATION ANALYSIS")
    print("="*60)

    # ==========================================
    # QUERY 1: Product Rating Evolution
    # ==========================================
    print("\n1. Analyzing product rating evolution...")

    query_ratings = """
    SELECT
        p.name,
        r.iteration,
        AVG(r.rating) as avg_rating,
        COUNT(*) as review_count,
        SUM(CASE WHEN r.is_fake THEN 1 ELSE 0 END) as fake_count
    FROM reviews r
    JOIN products p ON r.product_id = p.id
    GROUP BY p.name, r.iteration
    ORDER BY p.name, r.iteration
    """

    df_ratings = pd.read_sql_query(query_ratings, conn)

    # Plot: Rating evolution over time
    fig, ax = plt.subplots()

    for product in df_ratings['name'].unique():
        data = df_ratings[df_ratings['name'] == product]
        ax.plot(data['iteration'], data['avg_rating'], marker='o', label=product, linewidth=2)

    ax.set_xlabel('Iteration', fontsize=12)
    ax.set_ylabel('Average Rating (stars)', fontsize=12)
    ax.set_title('Product Rating Evolution Over Time', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Mark fake campaign period
    ax.axvspan(3, 4, alpha=0.2, color='red', label='Fake Campaign Burst')

    plt.tight_layout()
    output_file = Path(__file__).parent / "rating_evolution.png"
    plt.savefig(output_file, dpi=300)
    print(f"   Saved: {output_file}")

    # ==========================================
    # QUERY 2: Conversion Rate by Persona
    # ==========================================
    print("\n2. Analyzing conversion rates by persona...")

    query_conversion = """
    SELECT
        buyer_persona,
        decision,
        COUNT(*) as count
    FROM transactions
    GROUP BY buyer_persona, decision
    """

    df_conversion = pd.read_sql_query(query_conversion, conn)

    # Calculate percentages
    df_conv_pct = df_conversion.pivot(index='buyer_persona', columns='decision', values='count').fillna(0)
    df_conv_pct['total'] = df_conv_pct.sum(axis=1)
    df_conv_pct['buy_rate'] = (df_conv_pct.get('BUY', 0) / df_conv_pct['total']) * 100

    # Plot: Conversion rate by persona
    fig, ax = plt.subplots()
    personas = df_conv_pct.index
    buy_rates = df_conv_pct['buy_rate']

    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    bars = ax.bar(personas, buy_rates, color=colors, edgecolor='black', linewidth=1.5)

    ax.set_ylabel('Conversion Rate (%)', fontsize=12)
    ax.set_xlabel('Shopper Persona', fontsize=12)
    ax.set_title('Purchase Conversion Rate by Personality Type', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    output_file = Path(__file__).parent / "conversion_by_persona.png"
    plt.savefig(output_file, dpi=300)
    print(f"   Saved: {output_file}")

    # ==========================================
    # QUERY 3: Fake Review Impact
    # ==========================================
    print("\n3. Analyzing fake review impact...")

    query_impact = """
    SELECT
        p.name,
        AVG(CASE WHEN r.iteration <= 2 THEN r.rating ELSE NULL END) as baseline_rating,
        AVG(CASE WHEN r.iteration >= 3 THEN r.rating ELSE NULL END) as campaign_rating
    FROM reviews r
    JOIN products p ON r.product_id = p.id
    WHERE p.id IN (3, 5)
    GROUP BY p.name
    """

    df_impact = pd.read_sql_query(query_impact, conn)

    print("\n   Fake Review Impact Analysis:")
    print(df_impact.to_string(index=False))

    # ==========================================
    # SUMMARY STATISTICS
    # ==========================================
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    # Total reviews
    total_reviews = pd.read_sql_query("SELECT COUNT(*) as count FROM reviews", conn).iloc[0]['count']
    total_fake = pd.read_sql_query("SELECT COUNT(*) as count FROM reviews WHERE is_fake=1", conn).iloc[0]['count']
    fake_ratio = (total_fake / total_reviews) * 100 if total_reviews > 0 else 0

    print(f"\nTotal Reviews: {total_reviews}")
    print(f"Fake Reviews: {total_fake} ({fake_ratio:.1f}%)")

    # Conversion by iteration
    conv_by_iter = pd.read_sql_query("""
        SELECT
            iteration,
            SUM(CASE WHEN decision='BUY' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as buy_rate
        FROM transactions
        GROUP BY iteration
        ORDER BY iteration
    """, conn)

    print("\nConversion Rate by Iteration:")
    print(conv_by_iter.to_string(index=False))

    conn.close()
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
