# analysis/csv_analysis.py
# Comprehensive CSV-based analysis for MESA simulation results
# Includes per-persona, per-product, per-iteration purchase analysis

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10


class CSVAnalyzer:
    """
    Comprehensive analyzer for MESA simulation CSV exports

    Analyzes:
    - Purchase behavior per persona per product per iteration
    - Fake review impact on conversion rates (RQ1)
    - Persona vulnerability comparison (RQ2)
    - Temporal dynamics of rating manipulation
    """

    def __init__(self, results_dir: str = "data/results"):
        """
        Initialize analyzer

        Args:
            results_dir: Directory containing CSV exports
        """
        self.results_dir = Path(results_dir)
        self.reviews_df = None
        self.transactions_df = None
        self.metrics_df = None

        # Configuration (should match config.py)
        self.fake_targets = [3, 5]  # BudgetBeats, ClearSound Basic
        self.burst_iterations = [4, 5]
        self.personas = ["Impulsive", "Careful", "Skeptical"]
        self.products = {
            1: "SoundMax Pro (High)",
            2: "AudioBlast Wireless (Med-High)",
            3: "BudgetBeats (Low)",
            4: "TechWave Elite (Premium)",
            5: "ClearSound Basic (Low-Med)"
        }

        print("="*80)
        print("CSV-BASED COMPREHENSIVE ANALYSIS")
        print("="*80)

    def load_latest_data(self):
        """Load most recent CSV exports"""
        print("\n[1] Loading CSV data...")

        # Find latest files
        reviews_files = sorted(self.results_dir.glob("reviews_*.csv"))
        transactions_files = sorted(self.results_dir.glob("transactions_*.csv"))
        metrics_files = sorted(self.results_dir.glob("model_metrics_*.csv"))

        if not reviews_files or not transactions_files:
            raise FileNotFoundError(
                f"No CSV files found in {self.results_dir}\n"
                "Run simulation first: python main.py"
            )

        # Load latest
        self.reviews_df = pd.read_csv(reviews_files[-1], encoding='utf-8')
        self.transactions_df = pd.read_csv(transactions_files[-1], encoding='utf-8')

        if metrics_files:
            self.metrics_df = pd.read_csv(metrics_files[-1], index_col=0)

        print(f"  ✓ Reviews: {len(self.reviews_df)} records")
        print(f"  ✓ Transactions: {len(self.transactions_df)} records")
        if self.metrics_df is not None:
            print(f"  ✓ Metrics: {len(self.metrics_df)} iterations")

        # Data validation
        self._validate_data()

    def _validate_data(self):
        """Validate loaded data"""
        required_review_cols = ['product_id', 'rating', 'is_fake', 'iteration']
        required_trans_cols = ['product_id', 'persona', 'decision', 'iteration']

        for col in required_review_cols:
            if col not in self.reviews_df.columns:
                raise ValueError(f"Missing column in reviews: {col}")

        for col in required_trans_cols:
            if col not in self.transactions_df.columns:
                raise ValueError(f"Missing column in transactions: {col}")

        print("  ✓ Data validation passed")

    def analyze_purchases_per_persona_product_iteration(self):
        """
        DETAILED ANALYSIS: Purchase count per persona, per product, per iteration

        Returns:
            DataFrame with columns: iteration, product_id, persona, total_evals, purchases, conversion_rate
        """
        print("\n[2] Analyzing purchases per persona/product/iteration...")

        results = []

        for iteration in sorted(self.transactions_df['iteration'].unique()):
            iter_data = self.transactions_df[self.transactions_df['iteration'] == iteration]

            for product_id in sorted(self.transactions_df['product_id'].unique()):
                product_data = iter_data[iter_data['product_id'] == product_id]

                for persona in self.personas:
                    persona_data = product_data[product_data['persona'] == persona]

                    total_evals = len(persona_data)
                    purchases = (persona_data['decision'] == 'BUY').sum()
                    conversion = (purchases / total_evals * 100) if total_evals > 0 else 0

                    results.append({
                        'iteration': iteration,
                        'product_id': product_id,
                        'product_name': self.products[product_id],
                        'persona': persona,
                        'total_evaluations': total_evals,
                        'purchases': purchases,
                        'conversion_rate': conversion
                    })

        df = pd.DataFrame(results)

        # Save to CSV
        output_path = self.results_dir.parent / "analysis" / "purchases_detailed.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"  ✓ Saved detailed purchases to: {output_path}")

        return df

    def analyze_per_persona_summary(self, detailed_df):
        """
        Per-persona summary across all products and iterations

        Args:
            detailed_df: Output from analyze_purchases_per_persona_product_iteration

        Returns:
            DataFrame with persona-level aggregates
        """
        print("\n[3] Creating per-persona summary...")

        summary = []

        for persona in self.personas:
            persona_data = detailed_df[detailed_df['persona'] == persona]

            total_evals = persona_data['total_evaluations'].sum()
            total_purchases = persona_data['purchases'].sum()
            avg_conversion = (total_purchases / total_evals * 100) if total_evals > 0 else 0

            # Baseline (pre-burst) vs Burst vs Post-burst
            baseline = persona_data[~persona_data['iteration'].isin(self.burst_iterations +
                                    list(range(max(self.burst_iterations)+1, 21)))]
            burst = persona_data[persona_data['iteration'].isin(self.burst_iterations)]
            post_burst = persona_data[persona_data['iteration'] > max(self.burst_iterations)]

            baseline_conv = (baseline['purchases'].sum() / baseline['total_evaluations'].sum() * 100) \
                           if baseline['total_evaluations'].sum() > 0 else 0
            burst_conv = (burst['purchases'].sum() / burst['total_evaluations'].sum() * 100) \
                        if burst['total_evaluations'].sum() > 0 else 0
            post_conv = (post_burst['purchases'].sum() / post_burst['total_evaluations'].sum() * 100) \
                       if post_burst['total_evaluations'].sum() > 0 else 0

            summary.append({
                'persona': persona,
                'total_evaluations': total_evals,
                'total_purchases': total_purchases,
                'overall_conversion_%': round(avg_conversion, 2),
                'baseline_conversion_%': round(baseline_conv, 2),
                'burst_conversion_%': round(burst_conv, 2),
                'post_burst_conversion_%': round(post_conv, 2),
                'burst_impact_%': round(burst_conv - baseline_conv, 2)
            })

        df = pd.DataFrame(summary)

        # Save
        output_path = self.results_dir.parent / "analysis" / "persona_summary.csv"
        df.to_csv(output_path, index=False)
        print(f"  ✓ Saved persona summary to: {output_path}")

        return df

    def analyze_rq1_fake_impact(self):
        """
        RQ1: Impact of fake reviews on conversion rate for targeted products

        Returns:
            dict with statistical test results
        """
        print("\n[4] RQ1 Analysis: Fake Review Impact on Conversion Rate...")

        results = {}

        for target_id in self.fake_targets:
            product_name = self.products[target_id]
            print(f"\n  Analyzing: {product_name}")

            # Filter transactions for this product
            product_trans = self.transactions_df[self.transactions_df['product_id'] == target_id].copy()

            # Define phases
            baseline_iters = [i for i in range(1, min(self.burst_iterations))]
            burst_iters = self.burst_iterations
            post_iters = [i for i in range(max(self.burst_iterations)+1,
                          product_trans['iteration'].max()+1)]

            baseline_data = product_trans[product_trans['iteration'].isin(baseline_iters)]
            burst_data = product_trans[product_trans['iteration'].isin(burst_iters)]
            post_data = product_trans[product_trans['iteration'].isin(post_iters)]

            # Calculate conversion rates
            baseline_conv = (baseline_data['decision'] == 'BUY').sum() / len(baseline_data) * 100 \
                           if len(baseline_data) > 0 else 0
            burst_conv = (burst_data['decision'] == 'BUY').sum() / len(burst_data) * 100 \
                        if len(burst_data) > 0 else 0
            post_conv = (post_data['decision'] == 'BUY').sum() / len(post_data) * 100 \
                       if len(post_data) > 0 else 0

            # Chi-Square test: Baseline vs Burst
            baseline_buy = (baseline_data['decision'] == 'BUY').sum()
            baseline_nobuy = (baseline_data['decision'] == 'NO_BUY').sum()
            burst_buy = (burst_data['decision'] == 'BUY').sum()
            burst_nobuy = (burst_data['decision'] == 'NO_BUY').sum()

            contingency_table = [[baseline_buy, baseline_nobuy],
                                [burst_buy, burst_nobuy]]

            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

            # Cramér's V (effect size)
            n = baseline_buy + baseline_nobuy + burst_buy + burst_nobuy
            cramers_v = np.sqrt(chi2 / n) if n > 0 else 0

            results[target_id] = {
                'product_name': product_name,
                'baseline_conversion_%': round(baseline_conv, 2),
                'burst_conversion_%': round(burst_conv, 2),
                'post_burst_conversion_%': round(post_conv, 2),
                'absolute_increase_%': round(burst_conv - baseline_conv, 2),
                'relative_increase_%': round((burst_conv - baseline_conv) / baseline_conv * 100, 2)
                                      if baseline_conv > 0 else 0,
                'chi2_statistic': round(chi2, 4),
                'p_value': p_value,
                'cramers_v': round(cramers_v, 3),
                'significance': 'YES' if p_value < 0.05 else 'NO',
                'sample_size_baseline': len(baseline_data),
                'sample_size_burst': len(burst_data)
            }

            print(f"    Baseline: {baseline_conv:.1f}%")
            print(f"    Burst: {burst_conv:.1f}%")
            print(f"    Increase: +{burst_conv - baseline_conv:.1f}%")
            print(f"    Chi-Square: χ²={chi2:.2f}, p={p_value:.4f} {'***' if p_value < 0.001 else ''}")
            print(f"    Effect Size (Cramér's V): {cramers_v:.3f}")

        # Save
        df = pd.DataFrame(results).T
        output_path = self.results_dir.parent / "analysis" / "rq1_results.csv"
        df.to_csv(output_path, encoding='utf-8')
        print(f"\n  ✓ Saved RQ1 results to: {output_path}")

        return results

    def analyze_rq2_persona_vulnerability(self):
        """
        RQ2: Which persona is most vulnerable to fake reviews?

        Returns:
            dict with ANOVA results
        """
        print("\n[5] RQ2 Analysis: Persona Vulnerability Comparison...")

        # Calculate per-persona impact on targeted products
        persona_impacts = []

        for persona in self.personas:
            persona_data = self.transactions_df[
                (self.transactions_df['persona'] == persona) &
                (self.transactions_df['product_id'].isin(self.fake_targets))
            ]

            baseline = persona_data[~persona_data['iteration'].isin(
                self.burst_iterations + list(range(max(self.burst_iterations)+1, 21))
            )]
            burst = persona_data[persona_data['iteration'].isin(self.burst_iterations)]

            baseline_conv = (baseline['decision'] == 'BUY').sum() / len(baseline) * 100 \
                           if len(baseline) > 0 else 0
            burst_conv = (burst['decision'] == 'BUY').sum() / len(burst) * 100 \
                        if len(burst) > 0 else 0

            impact = burst_conv - baseline_conv

            persona_impacts.append({
                'persona': persona,
                'baseline_conversion_%': round(baseline_conv, 2),
                'burst_conversion_%': round(burst_conv, 2),
                'impact_%': round(impact, 2),
                'sample_size': len(persona_data)
            })

        df = pd.DataFrame(persona_impacts).sort_values('impact_%', ascending=False)

        # ANOVA test
        groups = []
        for persona in self.personas:
            persona_data = self.transactions_df[
                (self.transactions_df['persona'] == persona) &
                (self.transactions_df['product_id'].isin(self.fake_targets)) &
                (self.transactions_df['iteration'].isin(self.burst_iterations))
            ]
            persona_data['buy_numeric'] = (persona_data['decision'] == 'BUY').astype(int)
            groups.append(persona_data['buy_numeric'].values)

        f_stat, p_value = stats.f_oneway(*groups)

        print(f"\n  Vulnerability Ranking (by impact during burst):")
        for idx, row in df.iterrows():
            print(f"    {row['persona']:12} Impact: +{row['impact_%']:>6.2f}% "
                  f"(Baseline: {row['baseline_conversion_%']:.1f}% → Burst: {row['burst_conversion_%']:.1f}%)")

        print(f"\n  ANOVA Test:")
        print(f"    F-statistic: {f_stat:.4f}")
        print(f"    p-value: {p_value:.4f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''}")
        print(f"    Significant difference: {'YES' if p_value < 0.05 else 'NO'}")

        # Save
        output_path = self.results_dir.parent / "analysis" / "rq2_results.csv"
        df.to_csv(output_path, index=False)
        print(f"\n  ✓ Saved RQ2 results to: {output_path}")

        return {
            'persona_impacts': df.to_dict('records'),
            'anova_f_stat': f_stat,
            'anova_p_value': p_value
        }

    def visualize_temporal_dynamics(self, detailed_df):
        """
        Create comprehensive temporal visualizations

        Args:
            detailed_df: Detailed purchase data per iteration
        """
        print("\n[6] Creating temporal dynamics visualizations...")

        fig = plt.figure(figsize=(20, 12))

        # 1. Conversion rate over time for targeted products (per persona)
        ax1 = plt.subplot(2, 3, 1)
        for target_id in self.fake_targets:
            for persona in self.personas:
                data = detailed_df[
                    (detailed_df['product_id'] == target_id) &
                    (detailed_df['persona'] == persona)
                ]
                ax1.plot(data['iteration'], data['conversion_rate'],
                        marker='o', label=f"{self.products[target_id].split()[0]} - {persona}",
                        linewidth=2)

        # Mark burst iterations
        for burst_iter in self.burst_iterations:
            ax1.axvline(burst_iter, color='red', linestyle='--', alpha=0.3, linewidth=2)

        ax1.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Temporal Dynamics: Targeted Products by Persona', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=8, loc='best')
        ax1.grid(True, alpha=0.3)

        # 2. Aggregate conversion per persona over time
        ax2 = plt.subplot(2, 3, 2)
        for persona in self.personas:
            persona_data = detailed_df[detailed_df['persona'] == persona]
            iter_agg = persona_data.groupby('iteration').agg({
                'purchases': 'sum',
                'total_evaluations': 'sum'
            })
            iter_agg['conversion'] = iter_agg['purchases'] / iter_agg['total_evaluations'] * 100
            ax2.plot(iter_agg.index, iter_agg['conversion'], marker='s',
                    label=persona, linewidth=3, markersize=8)

        for burst_iter in self.burst_iterations:
            ax2.axvline(burst_iter, color='red', linestyle='--', alpha=0.3, linewidth=2)

        ax2.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Overall Conversion Rate (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Overall Persona Behavior Over Time', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)

        # 3. Heatmap: Conversion rate per product per iteration (all personas combined)
        ax3 = plt.subplot(2, 3, 3)
        pivot = detailed_df.groupby(['iteration', 'product_id'])['conversion_rate'].mean().reset_index()
        heatmap_data = pivot.pivot(index='product_id', columns='iteration', values='conversion_rate')

        sns.heatmap(heatmap_data, annot=False, cmap='RdYlGn', center=50,
                   cbar_kws={'label': 'Conversion Rate (%)'}, ax=ax3, vmin=0, vmax=100)
        ax3.set_ylabel('Product ID', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax3.set_title('Heatmap: Product Conversion Over Time', fontsize=14, fontweight='bold')

        # 4. Stacked bar: Purchases per persona per iteration
        ax4 = plt.subplot(2, 3, 4)
        pivot_purchases = detailed_df.groupby(['iteration', 'persona'])['purchases'].sum().unstack(fill_value=0)
        pivot_purchases.plot(kind='bar', stacked=True, ax=ax4, width=0.8,
                            color=['#ff9999', '#66b3ff', '#99ff99'])
        ax4.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Total Purchases', fontsize=12, fontweight='bold')
        ax4.set_title('Stacked Purchases per Iteration by Persona', fontsize=14, fontweight='bold')
        ax4.legend(title='Persona', fontsize=10)
        ax4.grid(True, alpha=0.3, axis='y')
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)

        # 5. Line plot: Targeted vs Non-targeted products
        ax5 = plt.subplot(2, 3, 5)
        targeted = detailed_df[detailed_df['product_id'].isin(self.fake_targets)]
        non_targeted = detailed_df[~detailed_df['product_id'].isin(self.fake_targets)]

        targeted_agg = targeted.groupby('iteration').agg({
            'purchases': 'sum',
            'total_evaluations': 'sum'
        })
        targeted_agg['conversion'] = targeted_agg['purchases'] / targeted_agg['total_evaluations'] * 100

        non_targeted_agg = non_targeted.groupby('iteration').agg({
            'purchases': 'sum',
            'total_evaluations': 'sum'
        })
        non_targeted_agg['conversion'] = non_targeted_agg['purchases'] / non_targeted_agg['total_evaluations'] * 100

        ax5.plot(targeted_agg.index, targeted_agg['conversion'], marker='o',
                label='Targeted Products', linewidth=3, color='red', markersize=8)
        ax5.plot(non_targeted_agg.index, non_targeted_agg['conversion'], marker='s',
                label='Non-Targeted Products', linewidth=3, color='green', markersize=8)

        for burst_iter in self.burst_iterations:
            ax5.axvline(burst_iter, color='red', linestyle='--', alpha=0.3, linewidth=2)

        ax5.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        ax5.set_title('Targeted vs Non-Targeted Products', fontsize=14, fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)

        # 6. Box plot: Conversion rate distribution per persona
        ax6 = plt.subplot(2, 3, 6)
        burst_data = detailed_df[detailed_df['iteration'].isin(self.burst_iterations)]
        baseline_data = detailed_df[~detailed_df['iteration'].isin(
            self.burst_iterations + list(range(max(self.burst_iterations)+1, 21))
        )]

        # Prepare data for box plot
        box_data = []
        labels = []
        for persona in self.personas:
            baseline_vals = baseline_data[baseline_data['persona'] == persona]['conversion_rate'].values
            burst_vals = burst_data[burst_data['persona'] == persona]['conversion_rate'].values
            box_data.extend([baseline_vals, burst_vals])
            labels.extend([f'{persona}\nBaseline', f'{persona}\nBurst'])

        bp = ax6.boxplot(box_data, labels=labels, patch_artist=True, widths=0.6)

        # Color coding
        colors = ['lightblue', 'lightcoral'] * 3
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        ax6.set_ylabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        ax6.set_title('Conversion Rate Distribution: Baseline vs Burst', fontsize=14, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, fontsize=9)

        plt.tight_layout()

        # Save
        output_path = self.results_dir.parent / "analysis" / "temporal_dynamics.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved temporal dynamics to: {output_path}")
        plt.close()

    def visualize_per_persona_breakdown(self, detailed_df):
        """
        Create separate visualization for each persona showing all products

        Args:
            detailed_df: Detailed purchase data
        """
        print("\n[7] Creating per-persona breakdown visualizations...")

        for persona in self.personas:
            fig, axes = plt.subplots(2, 3, figsize=(18, 10))
            fig.suptitle(f'PERSONA: {persona.upper()} - Detailed Product Analysis',
                        fontsize=16, fontweight='bold', y=0.995)

            persona_data = detailed_df[detailed_df['persona'] == persona]

            # 1. Conversion rate over time for all products
            ax = axes[0, 0]
            for product_id in sorted(persona_data['product_id'].unique()):
                data = persona_data[persona_data['product_id'] == product_id]
                label = self.products[product_id]
                color = 'red' if product_id in self.fake_targets else 'blue'
                linewidth = 3 if product_id in self.fake_targets else 1.5
                ax.plot(data['iteration'], data['conversion_rate'],
                       marker='o', label=label, linewidth=linewidth,
                       color=color, alpha=0.7 if product_id not in self.fake_targets else 1.0)

            for burst_iter in self.burst_iterations:
                ax.axvline(burst_iter, color='red', linestyle='--', alpha=0.3, linewidth=2)

            ax.set_xlabel('Iteration', fontweight='bold')
            ax.set_ylabel('Conversion Rate (%)', fontweight='bold')
            ax.set_title(f'{persona}: Conversion Rate Over Time', fontweight='bold')
            ax.legend(fontsize=8, loc='best')
            ax.grid(True, alpha=0.3)

            # 2. Bar chart: Average conversion per product
            ax = axes[0, 1]
            product_avg = persona_data.groupby('product_id')['conversion_rate'].mean().sort_index()
            colors = ['red' if pid in self.fake_targets else 'steelblue'
                     for pid in product_avg.index]
            bars = ax.bar(range(len(product_avg)), product_avg.values, color=colors, alpha=0.7)
            ax.set_xticks(range(len(product_avg)))
            ax.set_xticklabels([self.products[pid].split()[0] for pid in product_avg.index],
                              rotation=45, ha='right')
            ax.set_ylabel('Average Conversion Rate (%)', fontweight='bold')
            ax.set_title(f'{persona}: Average Conversion per Product', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

            # 3. Heatmap: Conversion rate per product per iteration
            ax = axes[0, 2]
            heatmap_data = persona_data.pivot(index='product_id', columns='iteration',
                                             values='conversion_rate')
            sns.heatmap(heatmap_data, annot=False, cmap='RdYlGn', center=50,
                       cbar_kws={'label': 'Conv Rate (%)'}, ax=ax, vmin=0, vmax=100)
            ax.set_ylabel('Product ID', fontweight='bold')
            ax.set_xlabel('Iteration', fontweight='bold')
            ax.set_title(f'{persona}: Product×Iteration Heatmap', fontweight='bold')

            # 4. Line plot: Targeted products before/during/after
            ax = axes[1, 0]
            for target_id in self.fake_targets:
                data = persona_data[persona_data['product_id'] == target_id]
                ax.plot(data['iteration'], data['conversion_rate'],
                       marker='o', label=self.products[target_id], linewidth=3)

            for burst_iter in self.burst_iterations:
                ax.axvline(burst_iter, color='red', linestyle='--', alpha=0.5, linewidth=2)
                ax.axvspan(burst_iter-0.5, burst_iter+0.5, alpha=0.2, color='red')

            ax.set_xlabel('Iteration', fontweight='bold')
            ax.set_ylabel('Conversion Rate (%)', fontweight='bold')
            ax.set_title(f'{persona}: Targeted Products Detail', fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)

            # 5. Stacked area: Purchases per product over time
            ax = axes[1, 1]
            pivot_purchases = persona_data.pivot_table(index='iteration', columns='product_id',
                                                       values='purchases', fill_value=0)
            pivot_purchases.plot.area(ax=ax, alpha=0.6, stacked=True)
            ax.set_xlabel('Iteration', fontweight='bold')
            ax.set_ylabel('Cumulative Purchases', fontweight='bold')
            ax.set_title(f'{persona}: Purchase Volume Distribution', fontweight='bold')
            ax.legend([self.products[pid].split()[0] for pid in pivot_purchases.columns],
                     fontsize=8, loc='upper left')
            ax.grid(True, alpha=0.3, axis='y')

            # 6. Summary stats table
            ax = axes[1, 2]
            ax.axis('off')

            # Calculate summary statistics
            baseline_iters = [i for i in range(1, min(self.burst_iterations))]
            burst_iters = self.burst_iterations

            summary_data = []
            for product_id in sorted(persona_data['product_id'].unique()):
                prod_data = persona_data[persona_data['product_id'] == product_id]
                baseline = prod_data[prod_data['iteration'].isin(baseline_iters)]
                burst = prod_data[prod_data['iteration'].isin(burst_iters)]

                baseline_conv = baseline['conversion_rate'].mean() if len(baseline) > 0 else 0
                burst_conv = burst['conversion_rate'].mean() if len(burst) > 0 else 0
                change = burst_conv - baseline_conv

                summary_data.append([
                    self.products[product_id].split()[0],
                    f"{baseline_conv:.1f}%",
                    f"{burst_conv:.1f}%",
                    f"{change:+.1f}%"
                ])

            table = ax.table(cellText=summary_data,
                           colLabels=['Product', 'Baseline', 'Burst', 'Change'],
                           cellLoc='center',
                           loc='center',
                           bbox=[0, 0, 1, 1])
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 2)

            # Color header
            for i in range(4):
                table[(0, i)].set_facecolor('#4472C4')
                table[(0, i)].set_text_props(weight='bold', color='white')

            # Color targeted products
            for i, row in enumerate(summary_data, 1):
                if any(target_name in row[0] for target_name in
                      [self.products[t].split()[0] for t in self.fake_targets]):
                    for j in range(4):
                        table[(i, j)].set_facecolor('#FFE6E6')

            ax.set_title(f'{persona}: Summary Statistics', fontweight='bold', pad=20)

            plt.tight_layout()

            # Save
            output_path = self.results_dir.parent / "analysis" / f"persona_{persona.lower()}_breakdown.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"  ✓ Saved {persona} breakdown to: {output_path}")
            plt.close()

    def generate_text_report(self, rq1_results, rq2_results, persona_summary):
        """
        Generate comprehensive text report

        Args:
            rq1_results: RQ1 analysis results
            rq2_results: RQ2 analysis results
            persona_summary: Per-persona summary
        """
        print("\n[8] Generating text report...")

        report_path = self.results_dir.parent / "analysis" / "comprehensive_report.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("COMPREHENSIVE ANALYSIS REPORT\n")
            f.write("Fake Review ABM Simulation - MESA Framework\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            # Dataset summary
            f.write("DATASET SUMMARY\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Reviews: {len(self.reviews_df)}\n")
            f.write(f"  - Genuine: {(~self.reviews_df['is_fake']).sum()}\n")
            f.write(f"  - Fake: {self.reviews_df['is_fake'].sum()}\n")
            f.write(f"Total Transactions: {len(self.transactions_df)}\n")
            f.write(f"  - BUY decisions: {(self.transactions_df['decision'] == 'BUY').sum()}\n")
            f.write(f"  - NO_BUY decisions: {(self.transactions_df['decision'] == 'NO_BUY').sum()}\n")
            f.write(f"Iterations: {self.transactions_df['iteration'].max()}\n")
            f.write(f"Products: {len(self.products)}\n")
            f.write(f"Personas: {len(self.personas)}\n\n")

            # RQ1 Results
            f.write("\n" + "="*80 + "\n")
            f.write("RQ1: IMPACT OF FAKE REVIEWS ON CONVERSION RATE\n")
            f.write("="*80 + "\n\n")

            for target_id, result in rq1_results.items():
                f.write(f"Product: {result['product_name']}\n")
                f.write("-"*80 + "\n")
                f.write(f"Baseline Conversion:       {result['baseline_conversion_%']:>6.2f}%\n")
                f.write(f"Burst Conversion:          {result['burst_conversion_%']:>6.2f}%\n")
                f.write(f"Post-Burst Conversion:     {result['post_burst_conversion_%']:>6.2f}%\n")
                f.write(f"\n")
                f.write(f"Absolute Increase:         +{result['absolute_increase_%']:>5.2f}%\n")
                f.write(f"Relative Increase:         +{result['relative_increase_%']:>5.2f}%\n")
                f.write(f"\n")
                f.write(f"Statistical Test (Chi-Square):\n")
                f.write(f"  χ² = {result['chi2_statistic']:.4f}\n")
                f.write(f"  p-value = {result['p_value']:.6f}\n")
                f.write(f"  Cramér's V = {result['cramers_v']:.3f}\n")
                f.write(f"  Statistically Significant: {result['significance']}\n")
                f.write(f"  Sample Sizes: Baseline={result['sample_size_baseline']}, Burst={result['sample_size_burst']}\n")
                f.write("\n\n")

            # RQ2 Results
            f.write("="*80 + "\n")
            f.write("RQ2: PERSONA VULNERABILITY TO FAKE REVIEWS\n")
            f.write("="*80 + "\n\n")

            f.write("Vulnerability Ranking (Impact during burst on targeted products):\n")
            f.write("-"*80 + "\n")
            for idx, persona_data in enumerate(rq2_results['persona_impacts'], 1):
                f.write(f"{idx}. {persona_data['persona']:12} "
                       f"Impact: +{persona_data['impact_%']:>6.2f}% "
                       f"(Baseline: {persona_data['baseline_conversion_%']:.1f}% → "
                       f"Burst: {persona_data['burst_conversion_%']:.1f}%)\n")

            f.write(f"\nANOVA Test:\n")
            f.write(f"  F-statistic = {rq2_results['anova_f_stat']:.4f}\n")
            f.write(f"  p-value = {rq2_results['anova_p_value']:.6f}\n")
            f.write(f"  Significant difference between personas: ")
            f.write(f"{'YES' if rq2_results['anova_p_value'] < 0.05 else 'NO'}\n")
            f.write("\n\n")

            # Persona Summary
            f.write("="*80 + "\n")
            f.write("OVERALL PERSONA BEHAVIOR SUMMARY\n")
            f.write("="*80 + "\n\n")

            for _, row in persona_summary.iterrows():
                f.write(f"Persona: {row['persona']}\n")
                f.write("-"*80 + "\n")
                f.write(f"Total Evaluations:          {row['total_evaluations']}\n")
                f.write(f"Total Purchases:            {row['total_purchases']}\n")
                f.write(f"Overall Conversion:         {row['overall_conversion_%']:.2f}%\n")
                f.write(f"Baseline Conversion:        {row['baseline_conversion_%']:.2f}%\n")
                f.write(f"Burst Conversion:           {row['burst_conversion_%']:.2f}%\n")
                f.write(f"Post-Burst Conversion:      {row['post_burst_conversion_%']:.2f}%\n")
                f.write(f"Burst Impact:               {row['burst_impact_%']:+.2f}%\n")
                f.write("\n")

            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")

        print(f"  ✓ Saved comprehensive report to: {report_path}")

    def run_full_analysis(self):
        """
        Execute complete analysis pipeline
        """
        print("\n" + "="*80)
        print("STARTING FULL ANALYSIS PIPELINE")
        print("="*80)

        # Load data
        self.load_latest_data()

        # Detailed purchase analysis
        detailed_df = self.analyze_purchases_per_persona_product_iteration()

        # Per-persona summary
        persona_summary = self.analyze_per_persona_summary(detailed_df)

        # RQ1 Analysis
        rq1_results = self.analyze_rq1_fake_impact()

        # RQ2 Analysis
        rq2_results = self.analyze_rq2_persona_vulnerability()

        # Visualizations
        self.visualize_temporal_dynamics(detailed_df)
        self.visualize_per_persona_breakdown(detailed_df)

        # Text report
        self.generate_text_report(rq1_results, rq2_results, persona_summary)

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\nOutput files saved to: {self.results_dir.parent / 'analysis'}")
        print("\nGenerated files:")
        print("  - purchases_detailed.csv (per-iteration breakdown)")
        print("  - persona_summary.csv (aggregate statistics)")
        print("  - rq1_results.csv (fake review impact)")
        print("  - rq2_results.csv (persona vulnerability)")
        print("  - temporal_dynamics.png (6-panel visualization)")
        print("  - persona_impulsive_breakdown.png")
        print("  - persona_careful_breakdown.png")
        print("  - persona_skeptical_breakdown.png")
        print("  - comprehensive_report.txt (detailed text report)")
        print("="*80 + "\n")


def main():
    """Main entry point"""
    try:
        analyzer = CSVAnalyzer()
        analyzer.run_full_analysis()

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease run the simulation first:")
        print("  python main.py")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
